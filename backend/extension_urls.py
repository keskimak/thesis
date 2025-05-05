# No class definition needed - these are module-level constants and functions
# To use these in another file, simply import like:
# from extension_urls import CONTINUUM_EXTENSION, get_extension_url
# or 
# import extension_urls

# FHIR Extension URLs used across the application
# These constants provide a centralized place to manage FHIR extension URLs

# Continuum extension URL
CONTINUUM_EXTENSION = "http://resepti.kanta.fi/fhir/StructureDefinition/extension/continuum"
MEDICINE_ID_EXTENSION = "medicineId"
MEDICINE_ID_PART_EXTENSION = "medicineIdPart"
ADVERSE_EFFECTS_EXTENSION = "http://resepti.kanta.fi/fhir/StructureDefinition/extension/adverseEffect"
INDICATIONS_EXTENSION = "http://resepti.kanta.fi/fhir/StructureDefinition/extension/structuredIndication"

# Profile URLs
MEDICATION_LIST_PROFILE = "http://resepti.kanta.fi/fhir/StructureDefinition/MedicationListMedicationRequest"

# Base FHIR server URL
FHIR_SERVER_BASE = "https://hapi.fhir.org/baseR4"

# Common extension URLs
MEDICATION_REQUEST_EXTENSIONS = {
    "CONTINUUM": CONTINUUM_EXTENSION,
    "PROFILE": MEDICATION_LIST_PROFILE,
    "MEDICINE_ID": MEDICINE_ID_EXTENSION,
    "MEDICINE_ID_PART": MEDICINE_ID_PART_EXTENSION,
    "ADVERSE_EFFECTS": ADVERSE_EFFECTS_EXTENSION,
    "INDICATIONS": INDICATIONS_EXTENSION,
}

# Helper function to get extension URL
def get_extension_url(extension_name: str) -> str:
    """
    Get the URL for a named extension.
    Args:
        extension_name: Name of the extension as defined in MEDICATION_REQUEST_EXTENSIONS
    Returns:
        str: The URL for the requested extension
    Raises:
        KeyError: If the extension name is not found
    """
    return MEDICATION_REQUEST_EXTENSIONS.get(extension_name)
