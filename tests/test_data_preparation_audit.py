"""Unabhängiges Inhaltsaudit: Manipulationen nur in Kopien echter V2-Dateien."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import data_preparation_audit as audit


class DataPreparationAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data,cls.meta=audit.load_data()

    def copies(self):
        return {name:frame.copy(deep=True) for name,frame in self.data.items()},copy.deepcopy(self.meta)

    def test_actual_v2_complete_audit(self):
        checks,metrics,arrays=audit.audit_content(self.data,self.meta)
        self.assertEqual(metrics['weekly_rows'],2600)
        self.assertEqual(metrics['zero_weeks'],558)
        self.assertEqual(metrics['total_minutes'],'422829.9')
        self.assertAlmostEqual(metrics['overestimation_pct'],27.32615083251715)
        self.assertEqual(len(checks),7)
        self.assertEqual(arrays['y'].shape,(100,9))

    def test_manipulated_total_detected(self):
        data,meta=self.copies()
        data['weekly'].loc[0,'activities_count']='1'
        with self.assertRaises(audit.AuditError):audit.audit_content(data,meta)

    def test_missing_zero_week_detected(self):
        data,meta=self.copies()
        zero=data['weekly'].index[data['weekly']['activities_count']=='0'][0]
        data['weekly']=data['weekly'].drop(index=zero)
        with self.assertRaises(audit.AuditError):audit.audit_content(data,meta)

    def test_wrong_split_boundaries_detected_even_with_same_counts(self):
        data,meta=self.copies()
        # Tausche nur U001/21 und U001/22, Größen 1800/400 bleiben gleich.
        train_row=data['train'].index[(data['train']['user_id']=='U001')&(data['train']['week_index']=='21')][0]
        test_row=data['test'].index[(data['test']['user_id']=='U001')&(data['test']['week_index']=='22')][0]
        old=data['train'].loc[train_row].copy()
        data['train'].loc[train_row]=data['test'].loc[test_row]
        data['test'].loc[test_row]=old
        with self.assertRaises(audit.AuditError):audit.audit_content(data,meta)

    def test_interpretation_feature_in_scaled_input_detected(self):
        data,meta=self.copies()
        data['scaled']['avg_duration_per_week']=data['kmeans']['avg_duration_per_week']
        with self.assertRaises(audit.AuditError):audit.audit_content(data,meta)

    def test_future_contamination_detected(self):
        data,meta=self.copies()
        data['regression'].loc[0,'avg_activities_last_4_weeks']='0.75'
        with self.assertRaises(audit.AuditError):audit.audit_content(data,meta)

    def test_wrong_scaling_parameter_detected(self):
        data,meta=self.copies()
        meta['params']['features']['share_running']['weight']=1.0
        with self.assertRaises(audit.AuditError):audit.audit_content(data,meta)

    def test_wrong_split_manifest_detected(self):
        data,meta=self.copies()
        meta['split']['test_target_weeks']=[22,23,24,25]
        with self.assertRaises(audit.AuditError):audit.audit_content(data,meta)


if __name__=='__main__':
    unittest.main()
