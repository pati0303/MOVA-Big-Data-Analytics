"""AP 2.2: real saved outputs for integration; synthetic boundary fixtures only in unit tests."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'src')]
import recommendation_engine as e
import ml_recommendation_rules as rules


class MLRecommendationsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = e.load_data(include_activity=True, include_catalog_extension=True)
        cls.actual = {uid: e.recommend_user(cls.data, uid, interests_permission=True, garmin_permission=True)
                      for uid in cls.data.users}

    def variants(self, uid, **kwargs):
        result = self.actual[uid]
        return e.recommendations(uid, self.data.offers, set(result['interest_categories']),
            self.data.approved_tags, result['profile']['sport_shares'],
            catalog_metadata=self.data.catalog_metadata, profile=result['profile'], **kwargs)

    def group_choice(self, uid, group, profile=None):
        result = self.actual[uid]
        ranked = e.rank_offers(self.data.offers, self.data.approved_tags, result['profile']['sport_shares'])
        rows, decisions = rules.select_variants(ranked, self.data.catalog_metadata,
                                               result['profile'] if profile is None else profile)
        return next(row[2] for row in rows if decisions[row[2]]['offer_group'] == group)

    def test_real_model_integration_changes_both_decisions(self):
        uid='U070'; profile=self.actual[uid]['profile']
        self.assertEqual(profile['segment_source'], 'stored_user_clusters')
        self.assertEqual(profile['source'], 'new_inference_saved_regression_model')
        self.assertEqual(profile['cluster_id'], int(self.data.clusters[uid]['cluster_id']))
        meta=json.loads((ROOT/'outputs/models/regression_linear_metadata.json').read_text())
        self.assertAlmostEqual(profile['regression_prediction'], meta['intercept'] + sum(
            profile['input_features'][f]*meta['coefficients'][f] for f in e.FEATURES), places=13)
        ids=lambda **kw:[r['offer_id'] for r in self.variants(uid, **kw)]
        self.assertEqual(ids(use_kmeans=False,use_regression=False), ['O001','O033','O035','O006','O004'])
        self.assertEqual(ids(use_kmeans=True,use_regression=False), ['O032','O033','O035','O006','O004'])
        self.assertEqual(ids(use_kmeans=False,use_regression=True), ['O001','O034','O035','O006','O004'])
        self.assertEqual(ids(), ['O032','O034','O035','O006','O004'])

    def test_occasional_and_frequent_variants_actual_profiles(self):
        for uid, shoes, sets, course in [('U070','O032','O037','O034'),('U044','O031','O036','O033')]:
            for group, expected in [('running_shoes',shoes),('hiking_sets',sets),('running_instruction',course)]:
                self.assertEqual(self.group_choice(uid,group),expected)

    def test_thresholds_and_invalid_predictions_unit_fixtures(self):
        # Values below are explicit unit-test inputs, never evaluation/demo profiles.
        ranked=e.rank_offers(self.data.offers,self.data.approved_tags,{'Running':1})
        for value, expected in [(1.999,'O033'),(2,'O033'),(2.999,'O033'),(3,'O034'),
                                (None,'O033'),(float('nan'),'O033'),(float('inf'),'O033'),
                                (-1,'O033'),(True,'O033'),('3','O033')]:
            profile=dict(prediction_status='available',regression_prediction=value)
            rows, decisions=rules.select_variants(ranked,self.data.catalog_metadata,profile)
            choice=next(row[2] for row in rows if decisions[row[2]]['offer_group']=='running_instruction')
            self.assertEqual(choice,expected)
        for status in ['permission_denied','model_unavailable_or_invalid']:
            p=dict(prediction_status=status,regression_prediction=3)
            rows,d=rules.select_variants(ranked,self.data.catalog_metadata,p)
            self.assertIn('O033',[r[2] for r in rows]);self.assertNotIn('O034',[r[2] for r in rows])

    def test_missing_invalid_cluster_falls_back_independently(self):
        for value in [None,True,'1',2,-1]:
            p=dict(self.actual['U070']['profile'],cluster_id=value)
            self.assertEqual(self.group_choice('U070','running_shoes',p),'O001')
            self.assertEqual(self.group_choice('U070','running_instruction',p),'O034')
        p=dict(self.actual['U070']['profile'],segment_status='permission_denied')
        self.assertEqual(self.group_choice('U070','running_shoes',p),'O001')

    def test_invalid_cluster_records_keep_reference_and_regression(self):
        reference=self.variants('U070',use_kmeans=False)
        invalid=[None, {}, {'user_id':'U070'}, {'cluster_id':'2'},
                 {'cluster_id':''}, {'segment_label':None},
                 {'cluster_id':None,'segment_label':None},
                 {'cluster_id':[], 'segment_label':None},
                 {'cluster_id':1,'segment_label':'Höhere Trainingshäufigkeit'},
                 {'cluster_id':'1'}, {'cluster_id':'0','segment_label':None},
                 {'cluster_id':'1','segment_label':'Geringere Trainingshäufigkeit'}]
        for record in invalid:
            with self.subTest(record=record):
                data=copy.copy(self.data);data.clusters=dict(self.data.clusters)
                data.clusters['U070']=record
                out=e.recommend_user(data,'U070',interests_permission=True,garmin_permission=True)
                profile=out['profile']
                self.assertIsNone(profile['cluster_id'])
                self.assertIsNone(profile['segment_label'])
                self.assertEqual(profile['segment_status'],'missing_or_ineligible')
                self.assertEqual(profile['segment_source'],'not_loaded')
                self.assertEqual(profile['prediction_status'],'available')
                self.assertEqual(out['recommendations'],reference)
                self.assertTrue(all(not o['kmeans_influence'] for o in out['recommendations']))

    def assert_model_load_fallback(self, error):
        from dashboard.services import user_context
        with patch('joblib.load',side_effect=error('explicit test fixture')):
            context=user_context('U070',interests_permission=True,garmin_permission=True)
        out=context['engine'];profile=out['profile']
        self.assertIsNotNone(context['activity'])
        self.assertIsNone(profile['regression_prediction'])
        self.assertEqual(profile['prediction_status'],'model_unavailable_or_invalid')
        self.assertEqual(profile['prediction_error_type'],error.__name__)
        self.assertEqual(profile['source'],'not_computed')
        self.assertEqual(profile['cluster_id'],self.actual['U070']['profile']['cluster_id'])
        self.assertEqual(out['recommendations'],self.variants('U070',use_regression=False))
        self.assertTrue(all(not o['regression_influence'] for o in out['recommendations']))
        self.assertTrue(any(o['kmeans_influence'] for o in out['recommendations']))

    def test_eoferror_model_load_falls_back_without_losing_context(self):
        self.assert_model_load_fallback(EOFError)

    def test_attributeerror_model_load_falls_back_without_losing_context(self):
        self.assert_model_load_fallback(AttributeError)

    def test_population_permissions_diversity_sports_and_determinism(self):
        for uid,result in self.actual.items():
            offers=result['recommendations'];profile=result['profile']
            self.assertLessEqual(len(offers),5)
            self.assertEqual(len(offers),len({o['offer_group'] for o in offers}))
            self.assertTrue(all(o['category'] in result['interest_categories'] for o in offers))
            shares=[o['historical_sport_share'] for o in offers]
            self.assertEqual(shares,sorted(shares,reverse=True))
            self.assertEqual(offers,self.variants(uid))
            reversed_offers=e.recommendations(uid,list(reversed(self.data.offers)),set(result['interest_categories']),
                self.data.approved_tags,profile['sport_shares'],catalog_metadata=self.data.catalog_metadata,profile=profile)
            self.assertEqual(offers,reversed_offers)
            for row in offers:
                if row['kmeans_influence']: self.assertIn('langfristiges Aktivitätssegment',row['match_reason'])
                if row['regression_influence']: self.assertIn('keine Teilnahmevoraussetzung',row['match_reason'])
                if self.data.catalog_metadata['offers'][row['offer_id']]['ml_rule'] is None:
                    self.assertFalse(row['kmeans_influence'] or row['regression_influence'])
            json.dumps(result,allow_nan=False)
        with patch.object(e,'verify_tracked_bytes',side_effect=AssertionError('denied read')), \
             patch('joblib.load',side_effect=AssertionError('denied model')):
            denied=e.run('U070',interests_permission=True,garmin_permission=False)
        self.assertTrue(all(not o['kmeans_influence'] and not o['regression_influence'] for o in denied['recommendations']))
        self.assertEqual(e.run('U070',interests_permission=False,garmin_permission=False)['recommendations'],[])
        self.assertEqual(self.actual['U023']['recommendations'],[])

    def test_neutral_offers_and_nonmatching_sports_unchanged(self):
        neutral=[o for o in self.data.offers if o['category']=='Wellness']
        outputs=[]
        for uid in ['U070','U044']:
            outputs.append(e.recommendations('FIXTURE',neutral,{'Wellness'},self.data.approved_tags,{},
                catalog_metadata=self.data.catalog_metadata,profile=self.actual[uid]['profile']))
        self.assertEqual(outputs[0],outputs[1])
        for uid in ['U070','U044']:
            rows,d=rules.select_variants(e.rank_offers(self.data.offers,self.data.approved_tags,{}),
                self.data.catalog_metadata,self.actual[uid]['profile'])
            self.assertTrue(all(not x['kmeans_influence'] and not x['regression_influence'] for x in d.values()))

    def test_catalog_and_invalid_metadata(self):
        self.assertEqual(len(self.data.offers),38)
        legacy=e.load_data()
        self.assertEqual(len(legacy.offers),30)
        self.assertEqual(self.data.offers[:30],legacy.offers)
        self.assertEqual({k:v for k,v in self.data.approved_tags.items() if k in legacy.approved_tags},legacy.approved_tags)
        import tempfile
        for kind in ['tag','mixed_group','double_signal','threshold','status']:
            policy=copy.deepcopy(self.data.catalog_metadata)
            if kind=='tag':policy['offers']['O002']['sport_tags']=['Strength']
            if kind=='mixed_group':policy['offers']['O036']['group']='running_shoes'
            if kind=='double_signal':policy['offers']['O033']['group']='running_shoes'
            if kind=='threshold':policy['thresholds']['single_below']=4
            if kind=='status':policy['offers']['O031']['status']='pending'
            with tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp);(root/'data/catalog').mkdir(parents=True)
                (root/'data/catalog/offers_extension_v1.csv').write_bytes((ROOT/'data/catalog/offers_extension_v1.csv').read_bytes())
                (root/'data/catalog/recommendation_metadata_v1.json').write_text(json.dumps(policy))
                with self.assertRaises(ValueError,msg=kind):rules.extend_catalog(root,legacy.offers,legacy.approved_tags)

    def test_preserved_data_models_metrics_and_references(self):
        manifest=json.loads((ROOT/'documentation/ml_recommendations_preservation_v1.json').read_text())
        for path, expected in manifest['sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),expected,path)

    def test_evaluation_artifacts_and_actual_outputs(self):
        saved=json.loads((ROOT/'outputs/ml_recommendations_v1/comparison.json').read_text())
        self.assertEqual(len(saved['users']),100)
        for row in saved['users']:
            actual_profile = self.actual[row['user_id']]['profile']
            # Only inference rounding may differ: observed <=2 binary64 ULPs
            # (8.88e-16). Keep every other profile field and all offers exact.
            self.assertEqual({k:v for k,v in row['profile'].items() if k != 'regression_prediction'},
                             {k:v for k,v in actual_profile.items() if k != 'regression_prediction'})
            self.assertAlmostEqual(row['profile']['regression_prediction'],
                                   actual_profile['regression_prediction'], delta=1e-15,
                                   msg=f"{row['user_id']}: regression inference rounding")
            for mode,flags in {'no_ml':(False,False),'kmeans_only':(True,False),
                               'regression_only':(False,True),'both':(True,True)}.items():
                self.assertEqual(row['variants'][mode],self.variants(row['user_id'],
                    use_kmeans=flags[0],use_regression=flags[1]))
        manifest=json.loads((ROOT/'outputs/ml_recommendations_v1/manifest.json').read_text())
        for path,expected in manifest['source_sha256'].items():
            if path.startswith('src/'):
                # Preserve AP-2.4 source provenance; current outputs are replayed above.
                import subprocess
                payload=subprocess.check_output(['git','-C',str(ROOT),'show',
                    f'2141d9480343e68e83405b385127dd3b85b791b2:{path}'])
            else:
                payload=(ROOT/path).read_bytes()
            self.assertEqual(hashlib.sha256(payload).hexdigest(),expected,path)
        for name,expected in manifest['artifact_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/'outputs/ml_recommendations_v1'/name).read_bytes()).hexdigest(),expected)

    def test_no_training_during_live_calls(self):
        with patch('sklearn.cluster.KMeans.fit',side_effect=AssertionError('no training')), \
             patch('sklearn.linear_model.LinearRegression.fit',side_effect=AssertionError('no training')):
            for uid in ['U070','U044']:
                self.assertEqual(e.run(uid,interests_permission=True,garmin_permission=True),self.actual[uid])


class MLUserViewTests(unittest.TestCase):
    def test_model_load_errors_keep_user_view_and_recommendations(self):
        from streamlit.testing.v1 import AppTest
        app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
        app.selectbox[0].select('U070').run()
        for toggle in app.toggle:toggle.set_value(True)
        for error in [EOFError,AttributeError]:
            with self.subTest(error=error.__name__):
                with patch('joblib.load',side_effect=error('explicit test fixture')):
                    app.run()
                self.assertFalse(app.exception)
                self.assertFalse(app.error)
                cards=[x.value for x in app.markdown if 'class="mova-offer"' in x.value]
                expected=['O032','O033','O035','O006','O004']
                self.assertEqual(len(cards),5)
                self.assertTrue(all(oid in card for oid,card in zip(expected,cards)))
                self.assertTrue(any('Prognose nicht verfügbar' in x.value for x in app.markdown))
                self.assertFalse(any('drei Terminen pro Woche bevorzugt' in x for x in cards))

    def test_live_demo_explanations_and_revocation(self):
        from streamlit.testing.v1 import AppTest
        app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
        for uid, ids in [('U070',['O032','O034','O035','O006','O004']),
                        ('U044',['O009','O010','O036','O038','O006'])]:
            app.selectbox[0].select(uid).run()
            for toggle in app.toggle:toggle.set_value(True)
            app.run()
            self.assertFalse(app.exception)
            text='\n'.join(x.value for x in app.markdown)
            cards=[x.value for x in app.markdown if 'class="mova-offer"' in x.value]
            self.assertEqual(len(cards),5)
            self.assertTrue(all(oid in card for oid,card in zip(ids,cards)))
            self.assertIn('05.07.2026',text)
            if uid=='U070':
                self.assertIn('langfristiges Aktivitätssegment',text)
                self.assertIn('keine Teilnahmevoraussetzung',text)
            app.toggle[1].set_value(False).run()
            cards=[x.value for x in app.markdown if 'class="mova-offer"' in x.value]
            self.assertFalse(any('langfristiges Aktivitätssegment' in x or 'drei Terminen pro Woche bevorzugt' in x for x in cards))


if __name__=='__main__':unittest.main()
