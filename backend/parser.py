import json
import os
import requests
from fhir.resources.bundle import Bundle
from fhir.resources.medicationrequest import MedicationRequest
from fhir.resources.medication import Medication
from fhir.resources.medicationknowledge import MedicationKnowledge
from extension_urls import get_extension_url, FHIR_SERVER_BASE, MEDICATION_LIST_PROFILE, MEDICATION_REQUEST_EXTENSIONS

from typing import Dict, Any

class Parser:
    def __init__(self, file_path: str = "examples/sample_data_filtered.json"):
        self.file_path = file_path
        self.medication_requests = {}
        self.lists = {}
        self.medications = {}
        
    def parse_json_data(self):
        with open(self.file_path, 'r') as file:
            data = json.load(file)
            entries = data.get("entry", [])
            self.medication_requests = []
            for entry in entries:
                resource = entry.get("resource")
                if resource and resource.get("resourceType") == "MedicationRequest":
                    try:
                        mr = MedicationRequest(**resource)
                        self.medication_requests.append(mr)
                    except Exception as e:
                        print(f"Error parsing medication request: {e}")
            if len(self.medication_requests) == 0:
                print("No valid medication requests found for fhir.parser")
                self.parseManually()

    def parseManually(self):
        with open(self.file_path, 'r') as file:
            data = json.load(file)
            entries = data.get("entry", [])
            self.medication_requests = []
            times = 5
            counter = 0
            for i in range(times):
                for entry in entries:
                    resource = entry.get("resource")
                    medicine_id = None
                    medicine_id_part = None
                    atc_code = None
                    atc_name = None
                    strength = None
                    form = None
                    authored_on = None
                    status = None
                    product = None
                    
                    if resource and resource.get("resourceType") == "MedicationRequest":
                        counter += 1
                        status = resource.get("status")
                        authored_on = resource.get("authoredOn")
                        id = resource.get("id")
                        id = id.replace("urn:oid:","")
                        adverse_effects = []
                        indications = []
                        for ext in resource.get("extension"):
                            if ext.get("url") == "http://resepti.kanta.fi/fhir/StructureDefinition/extension/continuum":
                                for ext_item in ext.get("extension"):
                                    if ext_item.get("url") == "medicineId":
                                        medicine_id = ext_item.get("valueIdentifier").get("value")
                                        medicine_id=medicine_id.replace("urn:oid:","")
                                    if ext_item.get("url") == "medicineIdPart":
                                        medicine_id_part = ext_item.get("valuePositiveInt")
                                        
                
                            if ext.get("url") == "http://resepti.kanta.fi/fhir/StructureDefinition/extension/adverseEffect":
                                adverse_effects.append(ext.get("valueCoding"))

                            if ext.get("url") == "http://resepti.kanta.fi/fhir/StructureDefinition/extension/structuredIndication":
                                indication = ext.get("valueCoding").get("code")
                                print("indication: ", indication)
                                indications.append(indication)
                                
                        contained = resource.get("contained")
                        for item in contained:
                            if item.get("resourceType") == "Medication":
                                medication = item
                                atc_code = medication.get("code").get("coding")[0].get("code")
                                atc_display = medication.get("code").get("coding")[0].get("display")
                                extension = medication.get("extension")
                                for ext in extension:
                                    if ext.get("url") == "http://resepti.kanta.fi/StructureDefinition/extension/pharmaceuticalProductStrength":
                                      strength = ext.get("valueString")
                                medication["strength"] = strength
                                medication["atc_code"] = atc_code
                                medication["atc_display"] = atc_display
                                
                            if item.get("resourceType") == "MedicationKnowledge":
                                form = item.get("doseForm").get("text")
                                product = item.get("code").get("coding")[0].get("display")
                        mr = {
                        "id": id,
                        "product": product,
                        "strength": strength,
                        "form": form,
                        "status": status,
                        "authored_on": authored_on,
                        "adverse_effects": adverse_effects,
                        "indications": indications
                    }
                        # Initialize medicine_id entry if it doesn't exist
                        print("medicine_id: ", medicine_id, "counter: ", counter)
                        
                        print("löytyykö: ", self.medications.get(medicine_id))
                        if medicine_id not in self.medications:
                            
                            self.medications[medicine_id] = {
                                "medicine_id_part": [],
                                "atc_code": atc_code,
                                "atc_display": atc_display
                            }
                        # Append medicine_id_part only if not already present
                        if medicine_id in self.medications:
                            print("medicine_id in use: ", medicine_id)
                            
                            
                        if medicine_id_part not in self.medications[medicine_id]['medicine_id_part']:
                            print("medicine_id_part not in use: ", medicine_id_part)
                            self.medications[medicine_id]['medicine_id_part'] = {
                                medicine_id_part: {
                                    "medication_requests": [mr]
                                }
                            }
                        else:
                            print("medicine_id_part already in use: ", medicine_id_part)
                            self.medications[medicine_id]['medicine_id_part'][medicine_id_part]["medication_requests"].append(mr)
                                                                                    
                    

                #  print(self.medications)

            print("medicine ids in use: ",len(self.medications))
            print("counter: ", counter)
    def get_medications(self):
        return self.medications

parser = Parser()
parser.parse_json_data()

