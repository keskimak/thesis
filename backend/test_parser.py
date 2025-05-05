import unittest
import json
import os
from backend.MedicationListParser import MedicationListParser

class TestMedicationListParser(unittest.TestCase):
    def setUp(self):
        # Use the existing sample data file
        self.test_file_path = "./examples/sample_data.json"
        self.parser = MedicationListParser(self.test_file_path)
        
        # Load the expected data for comparison
        with open(self.test_file_path, 'r') as f:
            self.expected_data = json.load(f)

    def test_parse_json_data(self):
        data = self.parser.parse_json_data()
        self.assertIsNotNone(data)

    def test_file_not_found(self):
        parser = MedicationListParser("nonexistent.json")
        with self.assertRaises(FileNotFoundError):
            parser.parse_json_data()

if __name__ == '__main__':
    unittest.main() 