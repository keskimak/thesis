import json
import random
from datetime import datetime, timedelta
from extension_urls import MEDICATION_REQUEST_EXTENSIONS,get_extension_url
from MedicationListParser import MedicationListParser

class SampleGenerator:
    def __init__(self, file_path: str = "examples/sample_data.json", encoding ='utf-8'):
        self.file_path = file_path
        self.filtered_data = None
    
    def return_filtered_data_from_file(self):
        with open("examples/sample_data_filtered.json", 'r', encoding='utf-8') as file:
            return json.load(file)
        
    def return_filtered_data(self):
        return self.filtered_data


    def parse_json_data(self):
        """
        Parse JSON data from the specified file.
        Returns the parsed data as a dictionary.
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                
                bundle_data = json.load(file)
                bundle_data["entry"] = [
                    entry for entry in bundle_data["entry"] 
                    if is_medication_request(entry)
                ]
                print("Entries: ",len(bundle_data["entry"]))
                print("Total: ", str (bundle_data["total"]))
                # Filter out MedicationDispense entries from the bundle data
                for entry in bundle_data["entry"]:
                    if entry.get("resource").get("resourceType") == "MedicationRequest" :
                        entry = correct_additional_instructions(entry)
                        category = entry.get("resource").get("category")
                        print("category: ", category)
                        extension = entry.get("resource").get("extension")
                        # Create a list of extensions to remove
                        urls_to_remove = [
                            "http://resepti.kanta.fi/fhir/StructureDefinition/extension/adverseEffect",
                            "http://resepti.kanta.fi/fhir/StructureDefinition/extension/structuredIndication"
                        ]
                        # Filter out the extensions we don't want
                        extension[:] = [ext for ext in extension if ext.get("url") not in urls_to_remove]
                        

                #parser = MedicationListParser(bundle_data)
                #parser.parse_json_data(bundle_data)
                print("Entries: ",len(bundle_data["entry"]))
                print("Total: ", str (bundle_data["total"]))
                if int(bundle_data["total"]) != len(bundle_data["entry"]):
                    bundle_data["total"] = len(bundle_data["entry"])
                    print("Updated Total: " + str (bundle_data["total"]))
                    for entry in bundle_data["entry"] :
                        
                                  self.filtered_data = bundle_data
            with open("examples/sample_data_filtered.json", "w", encoding='utf-8') as file:
                json.dump(bundle_data, file, indent=4)
            self.filtered_data = bundle_data
        except FileNotFoundError:
            print(f"File not found: {self.file_path}")
            return None




@staticmethod
def is_medication_request(entry) -> bool:
    resource_type = entry.get("resource", {}).get("resourceType")
    if resource_type == "MedicationRequest" and entry.get("resource", {}).get("meta").get("profile")[0] == "http://resepti.kanta.fi/fhir/StructureDefinition/MedicationListMedicationRequest":
        print("MedicationRequest: ", entry.get("resource", {}).get("id"))
        return True
    else:
        print("Not MedicationRequest: ", entry.get("resource", {}).get("id"))
        return False
    


def correct_additional_instructions(entry):
    dosageinstructions = entry.get("resource").get("dosageInstruction")
    if dosageinstructions is None:
        print("Dosage instructions not found")
        entry["resource"]["dosageInstruction"] = []
    else:
        for dosageinstruction in dosageinstructions:
            if dosageinstruction.get("additionalInstruction") is None:
                print("Additional instruction not found")
                dosageinstruction["additionalInstruction"] = []
            if dosageinstruction.get("additionalInstruction") is dict:
                
                print("Additional instruction is a dictionary")
                dosageinstruction["additionalInstruction"] = [dosageinstruction.get("additionalInstruction")]
    return entry

def random_datetime(start, end):
    """
    Generate a random datetime between two datetime objects.
    """
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    rand_dt = start + timedelta(seconds=random_seconds)
    formatted_dt = rand_dt.strftime("%m/%d/%Y %H:%M:%S")
    return formatted_dt

def generate_adverse_effects_and_indications(entry, atc_code):
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
        entry.get("resource").get("extension").append(adverse_effect)
    if ind is not None:
        indication = {
                        "url": "http://resepti.kanta.fi/fhir/StructureDefinition/extension/structuredIndication",
                        "valueCoding": {
                            "code": f"{ind["code"]}",
                            "display": f"{ind["display"]}",
                            "system": "urn:oid:1.2.246.537.6.1.1999"
                        }
                    }
        entry.get("resource").get("extension").append(indication)

    def duplicate_entry(self):
        data = self.return_filtered_data()
        
        if atc_code is not None:
                            if atc_code == "C09AA05":
                                print("atc_code: ", atc_code)
                                continuums = 2
                                for i in range(continuums):
                                    continuum_entry = entry.copy()
                            elif atc_code == "M01AE01":
                                print("atc_code: ", atc_code)
                            elif atc_code == "C10AA05":
                                print("atc_code: ", atc_code)

parser = SampleGenerator()
parser.parse_json_data()