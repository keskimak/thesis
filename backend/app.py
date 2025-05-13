from flask import Flask, jsonify, Response
from MedicationListParser import MedicationListParser  # <-- Your FHIR parser
from flask_cors import CORS
from parser import Parser
import json

app = Flask(__name__)
CORS(app)  # local development purposes
parser = Parser()
parser.parse_json_data()


# TODO: move to config
PATH_TO_EXAMPLE_DATA = "examples/sample_data_filtered.json"

# TODO: api address to config
@app.route('/api/medication-history', methods=['GET'])
def get_medication_history():
    parser = Parser()
    parser.parse_json_data()
    data = parser.get_continuums()
    
    # Use json.dumps with ensure_ascii=False to prevent Unicode escaping
    response = json.dumps(data, indent=4, ensure_ascii=False)
    return Response(response, mimetype='application/json; charset=utf-8')

if __name__ == "__main__":

    app.run(debug=True)
