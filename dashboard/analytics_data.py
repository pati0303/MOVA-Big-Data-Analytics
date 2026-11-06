"""Verified, request-scoped research views. No training, export or personal cache."""
from datetime import date, timedelta
from io import BytesIO
import hashlib
import importlib
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from dashboard.data_access import PROJECT_ROOT, DataAccessError

SOURCE_MANIFEST = 'documentation/ml_recommendations_preservation_v1.json'
K_VALUES = (2, 3, 6, 8)
RAW = 'data/raw/activities_simulated.csv'
WEEKS = 'data/processed/user_weekly_activities.csv'
FEATURES = 'data/processed/kmeans_user_features.csv'
SCALED = 'data/processed/kmeans_user_features_scaled.csv'
PREDICTIONS = 'outputs/tables/regression_test_predictions.csv'
BASELINE = 'outputs/tables/regression_baseline_comparison.csv'


class PermissionRequired(DataAccessError):
    pass


def require_garmin(permission):
    if permission is not True:
        raise PermissionRequired('Individuelle Analyse gesperrt: simulierte Garmin-Freigabe erforderlich.')


class ResearchData:
    """One render only. Full source frames never enter session state or st.cache."""
    def __init__(self, root=PROJECT_ROOT):
        self.root = Path(root)
        self._bytes = {}

    def verified_bytes(self, path):
        if path not in self._bytes:
            try:
                actual = (self.root / path).read_bytes()
                manifest = json.loads((self.root / SOURCE_MANIFEST).read_text())
                expected = manifest['sha256'][path]
                if hashlib.sha256(actual).hexdigest() != expected:
                    raise ValueError('Quellhash stimmt nicht mit dem bestätigten Projektbestand überein.')
                self._bytes[path] = actual
            except (OSError, ValueError, KeyError, TypeError) as exc:
                raise DataAccessError(f'Lab-Quelle fehlt oder ist nicht verifiziert: {path}') from exc
        return self._bytes[path]

    def table(self, path, columns=()):
        try:
            df = pd.read_csv(BytesIO(self.verified_bytes(path)),float_precision='round_trip')
            if not set(columns).issubset(df.columns):
                raise ValueError('Erforderliche Spalten fehlen.')
            return df
        except DataAccessError:
            raise
        except (ValueError, KeyError, pd.errors.ParserError) as exc:
            raise DataAccessError(f'Lab-Tabelle ist ungültig: {path}') from exc

    def metadata(self, path):
        try:
            return json.loads(self.verified_bytes(path))
        except (ValueError, TypeError) as exc:
            raise DataAccessError(f'Lab-Metadaten sind ungültig: {path}') from exc

    def understanding(self, sport=None):
        raw = self.table(RAW, ['user_id','date','sport_type','duration_min','distance_km'])
        raw['date'] = pd.to_datetime(raw['date'])
        chosen = raw if sport is None else raw[raw.sport_type == sport]
        weekly = chosen.assign(week_start=chosen.date-pd.to_timedelta(chosen.date.dt.weekday,unit='D'))
        series = weekly.groupby('week_start').size().reindex(pd.date_range('2026-01-05',periods=26,freq='7D'),fill_value=0)
        return dict(users=int(raw.user_id.nunique()),weeks=26,activities=len(raw),sports=sorted(raw.sport_type.unique()),
                    weekly_rows=len(self.table(WEEKS)),selected_count=len(chosen),share=len(chosen)/len(raw),
                    series=pd.DataFrame({'Wochenbeginn':series.index,'Aktivitäten':series.values}),
                    selected=chosen.drop(columns=['activity_id','user_id']))

    def zero_weeks(self, include=True):
        all_weeks = self.table(WEEKS, ['activities_count','week_index'])
        positive = all_weeks[all_weeks.activities_count > 0]
        current = all_weeks if include else positive
        mean_all = float(all_weeks.activities_count.mean())
        mean_active = float(positive.activities_count.mean())
        return dict(total=int(all_weeks.activities_count.sum()),n=len(current),zero_n=int((current.activities_count==0).sum()),
                    total_zero=int((all_weeks.activities_count==0).sum()),mean=float(current.activities_count.mean()),
                    all_mean=mean_all,active_mean=mean_active,relative_pct=(mean_active/mean_all-1)*100,
                    distribution=current.groupby('activities_count').size().rename('Nutzerwochen').reset_index(),
                    weekly=current.groupby('week_index').activities_count.mean().rename('Aktivitäten / Nutzerwoche').reset_index())

    def pipeline(self, step):
        steps = {
          'Rohaktivitäten': (RAW, None, 'Aktivitätszeilen aus der synthetischen V2; strukturelle Distanzleerwerte bleiben erhalten.'),
          'Auswahl / Prüfung': (RAW, 'data/processed/activities_selected.csv', 'Pflichtfelder, IDs, Daten und Sportgrenzen prüfen; distance_km aus Modellarbeitsdatei entfernen. Keine Zeilen gelöscht oder imputiert.'),
          'Wochenaggregation': ('data/processed/activities_selected.csv', WEEKS, 'Counts und Minuten je Nutzer/Woche aggregieren; Nutzer × 26 Wochen als vollständiges Raster, 558 echte Nullwochen.'),
          'K-Means-Features': ('data/processed/activities_selected.csv', FEATURES, 'Häufigkeit nutzt den Nenner 26; acht Sportanteile entstehen aus Aktivitätscounts. Minuten und Vielfalt dienen nur der Interpretation.'),
          'K-Means-Skalierung': (FEATURES, SCALED, 'Neun X-Spalten standardisieren, acht Sportkoordinaten anschließend mit 1/√8 gewichten. Gespeicherte Parameter, kein Refit.'),
          'Regressionsfeatures': (WEEKS, 'data/processed/regression_weekly_features.csv', 'X aus t und dem Mittel t−3…t, Ziel aus t+1. Frühe Wochen ohne Historie und letzte Woche ohne Ziel aus Trainingsbeispielen ausschließen.'),
          'Modellinputs / Split': ('data/processed/regression_weekly_features.csv', 'data/processed/regression_train.csv', 'Regression chronologisch 1.800 Training / 400 Test. K-Means nutzt separat die gewichtete 100×9-Matrix, keinen Regressionssplit.')}
        src,dst,why = steps[step]
        a = self.table(src); b = self.table(dst) if dst else a
        return dict(input=src,output=dst or src,input_shape=a.shape,output_shape=b.shape,why=why,
                    schema=pd.DataFrame({'Spalte':b.columns,'pandas-Datentyp':[str(t) for t in b.dtypes]}))

    def scaling(self, user_id, feature, *, garmin_permission):
        require_garmin(garmin_permission)
        raw = self.table(FEATURES); scaled = self.table(SCALED)
        params = self.metadata('outputs/models/kmeans_scaling_params.json')
        if feature not in params['feature_order']:raise DataAccessError('Unbekanntes Modellfeature.')
        selected = raw[raw.user_id==user_id]
        if len(selected)!=1:raise DataAccessError('Nutzerfeature fehlt oder ist nicht eindeutig.')
        source = str(PROJECT_ROOT/'src')
        if source not in sys.path:sys.path.insert(0,source)
        transform = importlib.import_module('data_preparation_scaling').transform_saved
        transformed = transform(selected.to_dict('records'),params)[0]
        x = float(selected.iloc[0][feature]); p = params['features'][feature]
        z = (x-p['mean'])/p['scale']
        weighted = float(transformed[params['feature_order'].index(feature)])
        saved = scaled.loc[scaled.user_id==user_id,feature]
        if len(saved)!=1 or not np.isclose(weighted,float(saved.iloc[0]),rtol=1e-10,atol=1e-10):
            raise DataAccessError('Transformation weicht vom gespeicherten Ergebnis ab.')
        activities = self.table(RAW);activities=activities[activities.user_id==user_id]
        return dict(x=x,mean=p['mean'],scale=p['scale'],weight=p['weight'],z=z,weighted=weighted,
                    raw_activities=activities[['date','sport_type','duration_min']],
                    features=selected.drop(columns='user_id'),scaled=scaled[scaled.user_id==user_id].drop(columns='user_id'))

    def split(self):
        m = self.metadata('documentation/regression_split_manifest.json')
        features = self.table('data/processed/regression_weekly_features.csv')
        train = self.table('data/processed/regression_train.csv');test=self.table('data/processed/regression_test.csv')
        if (len(features),len(train),len(test))!=(2200,1800,400):raise DataAccessError('Splitgrößen weichen ab.')
        return dict(manifest=m,all_rows=len(features),train_rows=len(train),test_rows=len(test))

    def kmeans(self, k):
        if k not in K_VALUES:raise DataAccessError('Nur gespeicherte Kandidaten k=2,3,6,8 verfügbar.')
        scores=self.table('outputs/tables/kmeans_k_selection.csv')
        stability=self.table('outputs/tables/kmeans_candidate_comparison.csv')
        return dict(scores=scores[scores.k.isin(K_VALUES)],selected=scores[scores.k==k].iloc[0],
                    stability=stability[stability.k==k].iloc[0],
                    profiles=self.table('outputs/tables/kmeans_final_cluster_profiles.csv'),
                    metadata=self.metadata('outputs/models/kmeans_final_metadata.json'))

    def cluster_for_user(self,user_id,*,garmin_permission):
        require_garmin(garmin_permission)
        df=self.table('data/processed/user_clusters.csv')
        row=df[df.user_id==user_id]
        if len(row)!=1:raise DataAccessError('Keine eindeutige gespeicherte Zuordnung verfügbar.')
        return row.iloc[0].to_dict()

    def regression_metadata(self):
        return self.metadata('outputs/models/regression_linear_metadata.json')

    def regression_case(self,user_id,input_week,*,garmin_permission):
        require_garmin(garmin_permission)
        pred=self.table(PREDICTIONS);base=self.table(BASELINE)
        p=pred[(pred.user_id==user_id)&(pred.week_index==input_week)]
        b=base[(base.user_id==user_id)&(base.week_index==input_week)]
        if len(p)!=1 or len(b)!=1:raise DataAccessError('Gespeicherter Testfall fehlt oder ist nicht eindeutig.')
        p=p.iloc[0];b=b.iloc[0];m=self.regression_metadata()
        contributions=[m['intercept']]+[float(p[f])*m['coefficients'][f] for f in m['feature_order']]
        if not np.isclose(sum(contributions),p.predicted_activities_next_week,atol=1e-12,rtol=1e-12):
            raise DataAccessError('Rechenschritte stimmen nicht mit gespeicherter Prognose überein.')
        if not np.isclose(p.predicted_activities_next_week,b.regression_prediction,atol=1e-12):
            raise DataAccessError('Test- und Baseline-Tabelle stimmen nicht überein.')
        weeks=self.table(WEEKS)
        history=weeks[(weeks.user_id==user_id)&weeks.week_index.between(input_week-3,input_week)].copy()
        if len(history)!=4 or not np.isclose(history.activities_count.mean(),p.avg_activities_last_4_weeks):
            raise DataAccessError('Vierwochenhistorie stimmt nicht mit Testeingaben überein.')
        cases=base[base.user_id==user_id].copy()
        return dict(prediction=p.to_dict(),baseline=b.to_dict(),metadata=m,contributions=contributions,
                    history=history.drop(columns='user_id'),user_cases=cases.drop(columns='user_id'))

    def evaluation(self,target_week=None,group='Alle Testfälle'):
        df=self.table(BASELINE,['actual_activities_next_week','regression_prediction','baseline_prediction'])
        if target_week is not None:df=df[df.week_index+1==target_week]
        if group=='Zielwoche = 0':df=df[df.actual_activities_next_week==0]
        elif group=='Zielwoche > 0':df=df[df.actual_activities_next_week>0]
        elif group!='Alle Testfälle':raise DataAccessError('Unbekannte Auswertungsgruppe.')
        if df.empty:raise DataAccessError('Keine Testfälle in dieser Auswahl.')
        rm=float(df.regression_absolute_error.mean());bm=float(df.baseline_absolute_error.mean())
        rrmse=float(np.sqrt(np.mean((df.regression_prediction-df.actual_activities_next_week)**2)))
        brmse=float(np.sqrt(np.mean((df.baseline_prediction-df.actual_activities_next_week)**2)))
        by_week=df.assign(Zielwoche=df.week_index+1).groupby('Zielwoche')[['actual_activities_next_week','regression_prediction','baseline_prediction','regression_absolute_error','baseline_absolute_error']].mean().reset_index()
        return dict(n=len(df),regression_mae=rm,baseline_mae=bm,regression_rmse=rrmse,baseline_rmse=brmse,
                    improvement_pct=(bm-rm)/bm*100 if bm else None,by_week=by_week)

    def recommendation_totals(self):
        m=self.metadata('outputs/tables/recommendation_before_after_summary.json')
        # Never return the individual examples embedded in the source JSON.
        keys=['users','slots_before','slots_after','tier_a_after','tier_b_after','tier_a_after_pct','users_with_tier_a','users_changed_pct','change_groups']
        return {key:m[key] for key in keys}

    def recommendation_case(self,user_id,*,garmin_permission,interests_permission):
        require_garmin(garmin_permission)
        if interests_permission is not True:raise PermissionRequired('Individuelle Angebote gesperrt: simulierte Interessenfreigabe erforderlich.')
        source=str(PROJECT_ROOT/'src')
        if source not in sys.path:sys.path.insert(0,source)
        engine=importlib.import_module('recommendation_engine')
        engine.permission_flags(interests_permission,garmin_permission)
        for path in ['data/raw/users_simulated.csv','data/raw/offers_simulated.csv',RAW,WEEKS,FEATURES,
                     'data/processed/user_clusters.csv','documentation/offer_sport_tags_approved.csv']:
            self.verified_bytes(path)
        data=engine.load_data(self.root,include_activity=True)
        categories=engine.interest_categories(engine.select_user(data,user_id))
        shares,status=engine.sport_profile(data,user_id,date(2026,7,5))
        if status!='available':raise DataAccessError('Das Sportprofil für den kontrollierten Vergleich ist nicht verfügbar.')
        before=engine.recommendations(user_id,data.offers,categories,{},shares)
        after=engine.recommendations(user_id,data.offers,categories,data.approved_tags,shares)
        saved=self.table('outputs/tables/recommendation_before_after_users.csv')
        row=saved[saved.user_id==user_id]
        if len(row)!=1:raise DataAccessError('Gespeicherter Vergleichsfall fehlt.')
        row=row.iloc[0]
        if ([o['offer_id'] for o in before]!=json.loads(row.top5_before) or
            [o['offer_id'] for o in after]!=json.loads(row.top5_after)):
            raise DataAccessError('Engine-Replay weicht vom gespeicherten Vergleich ab.')
        return dict(before=before,after=after,group=row.change_group)

    def iteration(self,metric):
        df=self.table('outputs/simulation_comparison/comparison_metrics.csv')
        label=df.columns[0]
        row=df[df[label]==metric]
        if len(row)!=1:raise DataAccessError('Vergleichsmetrik fehlt.')
        return pd.DataFrame({'Variante':['V1 historisch','Kontrolle 1,0','V2 1,3'],
                             'Wert':[float(row.iloc[0][key]) for key in ['V1_original','Kontrolle_1.0','V2_1.3']]})
