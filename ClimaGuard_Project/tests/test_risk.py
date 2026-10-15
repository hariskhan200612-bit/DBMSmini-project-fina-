import unittest
from climaguard.risk import risk_from_temperature, add_project_risk
import pandas as pd

class RiskTests(unittest.TestCase):
    def test_score_is_bounded(self):
        score, level = risk_from_temperature(50, 10, 20)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        self.assertEqual(level, "CRITICAL")

    def test_normal_example(self):
        score, level = risk_from_temperature(30, 0, 0)
        self.assertEqual(level, "NORMAL")
        self.assertEqual(score, 10)

    def test_dataframe_adds_columns_without_mutating_input(self):
        original = pd.DataFrame({"temp": [30, 45], "anomaly": [0, 5], "hot_days": [0, 4]})
        result = add_project_risk(original, "temp", "anomaly", "hot_days")
        self.assertIn("_Project_Risk_Score", result.columns)
        self.assertNotIn("_Project_Risk_Score", original.columns)
        self.assertEqual(result.iloc[1]["_Project_Risk_Level"], "CRITICAL")

if __name__ == "__main__":
    unittest.main()
