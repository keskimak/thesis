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
import copy

class Parser:
    def __init__(self, file_path: str = "examples/sample_data_filtered.json"):
        self.file_path = file_path
        self.medication_requests = {}
        self.lists = {}
        self.continuums = {}
        
    def parse_json_data(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            entries = data.get("entry", [])
            self.medication_requests = []
            for entry in entries:
                resource = entry.get("resource")
                if resource and resource.get("resourceType") == "MedicationRequest":
                    try:
                        # Decode any Unicode escape sequences in the resource
                        resource = json.loads(json.dumps(resource).encode('utf-8').decode('unicode-escape'))
                        print(resource)
                        mr = MedicationRequest(**resource)
                        self.medication_requests.append(mr)
                    except Exception as e:
                        print(f"Error parsing medication request: {e}")
            if len(self.medication_requests) == 0:
                print("No valid medication requests found for fhir.parser")
                self.parseManually()

    def parseManually(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            entries = data.get("entry", [])
            self.medication_requests = []
            times = 5
            counter = 0
            
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
                
                if resource and resource.get("resourceType") == "MedicationRequest" and resource.get("meta").get("profile")[0] == "http://resepti.kanta.fi/fhir/StructureDefinition/MedicationListMedicationRequest":
                    counter += 1
                    status = resource.get("status")
                    authored_on = resource.get("authoredOn")
                        # Example usage
                    start_date = datetime(2020, 1, 1)
                    end_date = datetime(2024, 12, 31)

                    authored_on = random_datetime(start_date, end_date)
                    if authored_on and " " in authored_on:
                        try:
                            dt = datetime.strptime(authored_on, "%d.%m.%Y %H:%M:%S")
                            authored_on = dt.strftime("%d.%m.%Y")
                        except ValueError:
                            pass  # Keep original if format doesn't match
                    id = resource.get("id")
                    id = id.replace("urn:oid:","")
                    
                    contained = resource.get("contained")
                    for item in contained:
                        if item.get("resourceType") == "Medication":
                            medication = item
                            atc_code = medication.get("code").get("coding")[0].get("code")
                            atc_display = medication.get("code").get("coding")[0].get("display")
                            # Debug print for atc_display
                            print("ATC Display:", atc_display)
                            extension = medication.get("extension")
                            for ext in extension:
                                if ext.get("url") == "http://resepti.kanta.fi/StructureDefinition/extension/pharmaceuticalProductStrength":
                                    strength = ext.get("valueString")
                                    # Debug print for strength
                                    print("Strength:", strength)
                        
                        if item.get("resourceType") == "MedicationKnowledge":
                            form = item.get("doseForm").get("text")
                            product = item.get("code").get("coding")[0].get("display")
                            # Debug print for form and product
                            print("Form:", form)
                            print("Product:", product)
                    adverse_effects = []
                    indications = []
                    generate_adverse_effects_and_indications(resource, atc_code)
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
                    
            self.create_duplicates()
            self.create_continuums()
            
            for continuum in self.continuums.values():
                for part in continuum["medicine_id_part"].values():
                    part["medication_requests"].sort(
                        key=lambda mr: datetime.strptime(mr["authored_on"], "%d.%m.%Y")
                        if mr.get("authored_on") else datetime.min,
                        reverse=True
                    )
            print("medicine ids in use: ",len(self.continuums))
            
    def get_continuums(self):
        return self.continuums

    def create_duplicates(self):
        duplicates = []
        for mr in self.medication_requests:
                if mr.get("atc_code") == "C09AA05":
                    print("mr duplicating: ", mr["medicine_id"])
                    duplicated1 = dict(mr)
                    duplicated1.pop("adverse_effects")
                    duplicated2 = dict(mr)
                    duplicated2.pop("adverse_effects")
                    duplicated3 = dict(mr)
                    duplicated3.pop("adverse_effects")
                    duplicated4 = dict(mr)
                    duplicated4.pop("adverse_effects")
                    
                    duplicated = copy.deepcopy(mr)
                    duplicated["medicine_id_part"] = str(random.randint(1728648970, 2111352112))
                    duplicated["strength"] = "5 mg"
                    duplicated.pop("adverse_effects")
                    print("duplicated emdiicneid: ", duplicated["medicine_id"])
                    duplicates.append(duplicated)
                    duplicates.append(duplicated1)
                    duplicates.append(duplicated2)
                    duplicates.append(duplicated3)
                    duplicates.append(duplicated4)
                    
                if mr.get("atc_code") == "C10AA05":
                    print("mr duplicating: ", mr["medicine_id"])
                    duplicated1 = dict(mr)
                    duplicated2 = dict(mr)
                    duplicates.append(duplicated1)
                    duplicates.append(duplicated2)
                    
        for duplicate in duplicates:
            self.medication_requests.append(duplicate)
        
        
        
    def create_continuums(self):
        self.medication_requests = ensure_unique_oid_ids(self.medication_requests)
        
        print("medication_requests: ", len(self.medication_requests))
        for mr in self.medication_requests:
            print("ID PART: ", mr.get("medicine_id_part"))
            print("ID: ", mr.get("medicine_id"))
        for mr in self.medication_requests:
            
            medicine_id = mr.get("medicine_id")
            medicine_id_part = mr.get("medicine_id_part")
            atc_code = mr.get("atc_code")
            atc_display = mr.get("atc_display")
            product = mr.get("product")
            strength = mr.get("strength")
            form = mr.get("form")
            authored_on = mr.get("authored_on")
            adverse_effects = mr.get("adverse_effects")
            indications = mr.get("indications")
            # Initialize medicine_id entry if it doesn't exist
            # Ensure medicine_id exists
            if medicine_id not in self.continuums:
                if medicine_id is None:
                    print("medicine_id is None: ", mr)
                print("Initializing new medicine_id: ", medicine_id)
                self.continuums[medicine_id] = {
                    "atc_code": atc_code,
                    "atc_display": atc_display,
                    "medicine_id_part": {}
                }
            else:
                print("medicine_id already exists: ", medicine_id)
            # Now handle medicine_id_part
            print("medicine_id_part: ", medicine_id_part)
       
            if medicine_id_part in self.continuums[medicine_id]["medicine_id_part"]:
                print("Appending to existing medicine_id_part: ", medicine_id_part)
                mr.pop("medicine_id_part")
                mr.pop("medicine_id")
                self.continuums[medicine_id]["medicine_id_part"][medicine_id_part]["medication_requests"].append(mr)
                
            if medicine_id_part not in self.continuums[medicine_id]["medicine_id_part"]:
                mr.pop("medicine_id_part")
                mr.pop("medicine_id")
                print("Initializing new medicine_id_part: ", medicine_id_part)
                self.continuums[medicine_id]["medicine_id_part"][medicine_id_part] = {"medication_requests": [mr]}
                
            
                        
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
    formatted_dt = rand_dt.strftime("%d.%m.%Y %H:%M:%S")
    return formatted_dt                  
    

def generate_adverse_effects_and_indications(entry, atc_code):
    print("atc_code: ", atc_code)
    icd_codes = {
        "headache": { "code": "R51.80", "display": "Päänsärky"},
        "blood_pressure": { "code": "I15", "display": "Sekundaar.korkea verenpaine"},
        "limb_pain": { "code": "M79.6", "display": "Raajakipu"},
        "dizzyness": { "code": "R42", "display": "Pyörrytys ja huimaus"},
        "cholesterol": {"code": "E78.0", "display": "Hyperkolesterolemia"},
    }
    adv = None
    ind = None
    if atc_code == "C09AA05":
        adv = icd_codes["dizzyness"]
        ind = icd_codes["blood_pressure"]
    elif atc_code == "M01AE01":
        adv = icd_codes["headache"]
        ind = icd_codes["limb_pain"]
    elif atc_code == "C10AA05":
        ind = icd_codes["cholesterol"]
    print("adv: ", adv)
    print("ind: ", ind)
    if adv is not None:
        adverse_effect = {
                    "url": "http://resepti.kanta.fi/fhir/StructureDefinition/extension/adverseEffect",
                    "valueCoding": {
                        "code": f"{adv["code"]}",
                        "display": f"{adv["display"]}",
                        "system": "urn:oid:1.2.246.537.6.1.1999"
                    }
                    }
        entry.get("extension").append(adverse_effect)
    if ind is not None:
        indication = {
                        "url": "http://resepti.kanta.fi/fhir/StructureDefinition/extension/structuredIndication",
                        "valueCoding": {
                            "code": f"{ind["code"]}",
                            "display": f"{ind["display"]}",
                            "system": "urn:oid:1.2.246.537.6.1.1999"
                        }
                    }
        entry.get("extension").append(indication)

parser = Parser()
parser.parse_json_data()
