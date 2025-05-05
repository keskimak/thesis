from flask import Flask, jsonify
from MedicationListParser import MedicationListParser  # <-- Your FHIR parser
from flask_cors import CORS
from parser import Parser

app = Flask(__name__)
CORS(app)  # local development purposes

# TODO: move to config
PATH_TO_EXAMPLE_DATA = "examples/sample_data_filtered.json"

# TODO: api address to config
@app.route('/api/medication-history', methods=['GET'])
def get_medication_history():
    parser = Parser()
    parser.parse_json_data()
    data = parser.get_medications()
    print("data: ", data)
    return jsonify(data) 

if __name__ == "__main__":
    app.run(debug=True)
