import json
import os
import requests
from fhir.resources.bundle import Bundle
from fhir.resources.medicationrequest import MedicationRequest
from fhir.resources.medication import Medication
from fhir.resources.medicationknowledge import MedicationKnowledge
from extension_urls import get_extension_url, FHIR_SERVER_BASE, MEDICATION_LIST_PROFILE, MEDICATION_REQUEST_EXTENSIONS

from typing import Dict, Any

class MedicationListParser:
    def __init__(self, file_path: str = "examples/sample_data_filtered.json"):
        self.file_path = file_path
        self.medication_requests = {}
        self.continuums = {}
        self.grouped_by_medicine_id = []
        self.grouped_by_medicine_id_and_medicine_id_part = []
        self.laakityslista = {"patient_id": "050566-909R"}

    def get_medication_requests(self):
        return self.medication_requests
    
    def get_laakityslista(self):
        return self.laakityslista

    def get_grouped_by_medicine_id(self):
        print("Grouped by medicine id: ", self.grouped_by_medicine_id)
        return self.grouped_by_medicine_id
    
    def get_grouped_by_medicine_id_and_medicine_id_part(self):
        return self.grouped_by_medicine_id_and_medicine_id_part
    
    def parse_json_data(self, data):
        """
        Parse JSON data from the specified file.
        Returns the parsed data as a dictionary.
        """
        try:
            
            if data is None:
                with open(self.file_path, 'r', encoding='utf-8') as file:
                    print("Parsing JSON data from file: ", self.file_path)
                    bundle_data = json.load(file)
            else:
                bundle_data = data
                
            bundle_medicine_ids = {}
            bundle_medicine_id_parts = {}
            medication_requests = {}
            bundle_info = {
                "medicine_id": {},
                "patient_id": "050566-909R"
            }
            # Extract only MedicationRequest resources
            for entry in bundle_data.get("entry"):
                    
                if entry.get("resource").get("resourceType") == "MedicationRequest":
                    mr = entry.get("resource")
                    mr_id = mr.get("id")
                    print("Medication request id: ", mr_id)
                    medicine_id = None
                    medicine_id_part = None
                    adverse_effects = []
                    indications = []
                    newest = False
                    # Build extension dictionary for easier access
                    ext_dict = self.build_extension_dict(mr)
                    # Group by medicine id and medicine id part
                    continuum_extension = ext_dict.get(MEDICATION_REQUEST_EXTENSIONS.get("CONTINUUM"))
                    if continuum_extension:
                        nested_extension = continuum_extension.get("extension")
                        for ext in nested_extension:
                            if ext.get("url") == MEDICATION_REQUEST_EXTENSIONS.get("MEDICINE_ID"):
                                medicine_id = ext.get("valueIdentifier").get("value")
                                medicine_id = medicine_id.replace("urn:oid:", "")
                            if ext.get("url") == MEDICATION_REQUEST_EXTENSIONS.get("MEDICINE_ID_PART"):
                                medicine_id_part = ext.get("valuePositiveInt")
                                print("medicine_id_part: ", medicine_id_part)
                            if ext.get("url") == "newest":
                                newest = ext.get("valueBoolean")
                                print("newest: ", newest)
                    adverse_effect_ext = ext_dict.get(MEDICATION_REQUEST_EXTENSIONS.get("ADVERSE_EFFECTS"))
                    if adverse_effect_ext:
                        adverse_effects.append(adverse_effect_ext.get("valueCoding"))

                    indication_ext = ext_dict.get(MEDICATION_REQUEST_EXTENSIONS.get("INDICATIONS"))
                    if indication_ext:
                        indications.append(indication_ext.get("valueCoding"))
                            
                    contained = mr.get("contained")
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
                    
                    medication_requests = mr_id,{
                        "id": mr_id,
                        "medicine_id": medicine_id,
                        "medicine_id_part": medicine_id_part,
                        # Add authored on date for sorting
                        "authored_on": mr.authoredOn if hasattr(mr, "authoredOn") else None,
                        # FHIR resource
                        "medication_request": mr,
                        "adverse_effects": adverse_effects,
                        "indications": indications,
                        
                        "medication": medication
                    }
                    print("bundle_info: ", bundle_info)
                    # Step 1: Make sure medicineId exists
                    if medicine_id not in bundle_info["medicine_id"]:
                        bundle_info["medicine_id"][medicine_id] = {
                            "atc_code": medication.get("atc_code"),
                            "atc_display": medication.get("atc_display"),
                            "medicine_id_part": {}   # <-- MUST be dict
                        }

                    if medicine_id_part not in bundle_info["medicine_id"][medicine_id]["medicine_id_part"]:
                        bundle_info["medicine_id"][medicine_id]["medicine_id_part"][medicine_id_part] = []
                        

                    bundle_info["medicine_id"][medicine_id]["medicine_id_part"][medicine_id_part].append(mr)
                    self.laakityslista = bundle_info
                    # self.validate_resources(resource)
            print("Parser: Medication requests: ", len(medication_requests)) 
            
            print(self.laakityslista)     
            self.medication_requests = medication_requests
            
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.file_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in file: {self.file_path}") 
        
    @staticmethod
    def build_extension_dict(resource):
        """Create a dictionary of extensions keyed by URL. for easier access"""
        extension_dict = {}
        for ext in resource.get("extension") or []:
            extension_dict[ext.get("url")] = ext
        return extension_dict
            
            
            
    def validate_resources(self, mr):        
        response = requests.post(
            f"{FHIR_SERVER_BASE}/MedicationRequest/$validate?profile={MEDICATION_LIST_PROFILE}",
            headers={"Content-Type": "application/fhir+json"},
            json=mr
        )
        print(response.json())

        
        
