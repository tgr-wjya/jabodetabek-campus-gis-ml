# test_model_and_pipeline.py
import unittest

from shapely.geometry import Point

from retrain_standalone import wgs_to_utm
from simplify_data import round_coords


class TestModelAndPipeline(unittest.TestCase):
    def test_round_coords_single_and_nested(self):
        coord = [106.84513, -6.20876]
        res = round_coords(coord)
        self.assertEqual(res, [106.84513, -6.20876])

        nested = [[106.1234567, -6.1234567], [107.9876543, -6.9876543]]
        res_nested = round_coords(nested)
        self.assertEqual(res_nested, [[106.12346, -6.12346], [107.98765, -6.98765]])

    def test_wgs_to_utm_reprojection(self):
        # Monas Jakarta coordinate in WGS84: ~ (106.8272, -6.1754)
        monas_wgs = Point(106.8272, -6.1754)
        monas_utm = wgs_to_utm(monas_wgs)
        
        # UTM 48S Easting should be around 702,000 m and Northing around 9,317,000 m
        self.assertAlmostEqual(monas_utm.x, 702419.0, delta=5000)
        self.assertAlmostEqual(monas_utm.y, 9317000.0, delta=5000)


if __name__ == "__main__":
    unittest.main()
