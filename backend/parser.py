import json
import os
import requests
from fhir.resources.bundle import Bundle
from fhir.resources.medicationrequest import MedicationRequest
from fhir.resources.medication import Medication
from fhir.resources.medicationknowledge import MedicationKnowledge
from extension_urls import get_extension_url, FHIR_SERVER_BASE, MEDICATION_LIST_PROFILE, MEDICATION_REQUEST_EXTENSIONS
from datetime import datetime, timedelta
from typing import Dict, Any
import random

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
                         # Example usage
                        start_date = datetime(2020, 1, 1)
                        end_date = datetime(2024, 12, 31)

                        authored_on = random_datetime(start_date, end_date)
                        if authored_on and " " in authored_on:
                            try:
                                dt = datetime.strptime(authored_on, "%m/%d/%Y %H:%M:%S")
                                authored_on = dt.strftime("%m/%d/%Y")
                            except ValueError:
                                pass  # Keep original if format doesn't match
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
                                        medicine_id_part = str(ext_item.get("valuePositiveInt"))
                                        
                
                            if ext.get("url") == "http://resepti.kanta.fi/fhir/StructureDefinition/extension/adverseEffect":
                                adverse_effects.append(ext.get("valueCoding"))

                            if ext.get("url") == "http://resepti.kanta.fi/fhir/StructureDefinition/extension/structuredIndication":
                                indication = ext.get("valueCoding")
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
                             
                                
                            if item.get("resourceType") == "MedicationKnowledge":
                                form = item.get("doseForm").get("text")
                                product = item.get("code").get("coding")[0].get("display")
                       
                        mr = {
                            "medicine_id": medicine_id,
                            "medicine_id_part": medicine_id_part,
                            "id": id,
                            "product": product,
                            "strength": strength,
                            "atc_code": atc_code,
                            "atc_display": atc_display,
                            "form": form,
                            "status": status,
                            "authored_on": authored_on,
                        "adverse_effects": adverse_effects,
                        "indications": indications
                    }
                        self.medication_requests.append(mr)
                        
                #  print(self.medications)
            self.create_continuums()
            for med in self.medications.values():
                for part in med["medicine_id_part"].values():
                    part["medication_requests"].sort(
                        key=lambda mr: datetime.strptime(mr["authored_on"], "%m/%d/%Y")
                        if mr.get("authored_on") else datetime.min
                    )
            print("medicine ids in use: ",len(self.medications))
            for medicine_id in self.medications:
                print("medicine_id: ", medicine_id)
                print("medicine_id_part: ", len(self.medications[medicine_id].get("medicine_id_part")))
            print("counter: ", counter)
    def get_medications(self):
        return self.medications

    def create_continuums(self):
        self.medication_requests = ensure_unique_oid_ids(self.medication_requests)
        print("medication_requests: ", len(self.medication_requests))
        for mr in self.medication_requests:
            medicine_id = mr.get("medicine_id")
            medicine_id_part = mr.get("medicine_id_part")
            atc_code = mr.get("atc_code")
            atc_display = mr.get("atc_display")
            product = mr.get("product")
            strength = mr.get("strength")
            form = mr.get("form")
            status = mr.get("status")
            authored_on = mr.get("authored_on")
            adverse_effects = mr.get("adverse_effects")
            indications = mr.get("indications")
        # Initialize medicine_id entry if it doesn't exist
            # Ensure medicine_id exists
            if medicine_id not in self.medications:
                print("Initializing new medicine_id: ", medicine_id)
                self.medications[medicine_id] = {
                    "atc_code": atc_code,
                    "atc_display": atc_display,
                    "medicine_id_part": {}
                }

            # Now handle medicine_id_part
            print("medicine_id_part: ", medicine_id_part)
            if medicine_id_part  in self.medications[medicine_id]["medicine_id_part"] and len(self.medications[medicine_id]["medicine_id_part"][medicine_id_part]["medication_requests"]) > 5:
                medicine_id_part = str(random.randint(1728648970, 2111352112))
                print("arvotaan " ,medicine_id_part)
                
            if medicine_id_part in self.medications[medicine_id]["medicine_id_part"]:
                print("Appending to existing medicine_id_part: ", medicine_id_part)
                self.medications[medicine_id]["medicine_id_part"][medicine_id_part]["medication_requests"].append(mr)
                
            if medicine_id_part not in self.medications[medicine_id]["medicine_id_part"]:
                print("Initializing new medicine_id_part: ", medicine_id_part)
                self.medications[medicine_id]["medicine_id_part"][medicine_id_part] = {"medication_requests": [mr]}
                
            
                        
def ensure_unique_oid_ids(objects):
    seen_ids = set()
    oid_root="1.2.246.10.11111111.93001.2024"
    for obj in objects:
        current_id = obj.get("id")
        if current_id in seen_ids or not current_id:
            # Generate a new unique OID by appending a random suffix
            new_id = f"{oid_root}.{random.randint(100000000000, 999999999999)}"
            while new_id in seen_ids:
                new_id = f"{oid_root}.{random.randint(100000000000, 999999999999)}"
            obj["id"] = new_id
        seen_ids.add(obj["id"])
    return objects        
  
def random_datetime(start, end):
    """
    Generate a random datetime between two datetime objects.
    """
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    rand_dt = start + timedelta(seconds=random_seconds)
    formatted_dt = rand_dt.strftime("%m/%d/%Y %H:%M:%S")
    return formatted_dt                  
    
parser = Parser()
parser.parse_json_data()

