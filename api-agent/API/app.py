from fastapi import FastAPI
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI()

# Define the request body schema
class IDApplicationInfo(BaseModel):
    childID: int
    biometricSector: str
    biometricDate: str
    placeOfCollection: str
    phone: str

id_applications = []
id_corrections = []

# Description for the POST route
@app.post("/id_application/", description="This route is used for applying for a new national ID.")
async def submit_id_application(applicant_info: IDApplicationInfo):
    record = {
        "message": "User information submitted successfully",
        "Child ID": applicant_info.childID,
        "Biometric Sector": applicant_info.biometricSector,
        "Biometric Date": applicant_info.biometricDate,
        "Place of Collection": applicant_info.placeOfCollection,
        "Phone Number": applicant_info.phone
    }
    id_applications.append(record)
    return record

@app.get("/get_id_application/", description="Retrieve all national ID application submissions")
async def get_all_id_applications():
    return {"applications": id_applications}

# Define the request body schema for ID correction
class IDCorrectionInfo(BaseModel):
    identificationDocumentNumber: str
    placeOfCollection: str
    reasonForIDCorrection: str
    districtProcessingOffice: str
    phone: str

# POST route for correcting an existing national ID
@app.post("/id_correction/", description="This route is used for applying for a national ID correction.")
async def correct_id_info(correction_info: IDCorrectionInfo):
    record = {
        "message": "National ID correction submitted successfully",
        "Identification Document Number": correction_info.identificationDocumentNumber,
        "Place of Collection": correction_info.placeOfCollection,
        "Reason for ID Correction": correction_info.reasonForIDCorrection,
        "District Processing Office": correction_info.districtProcessingOffice,
        "Phone Number": correction_info.phone
    }
    id_corrections.append(record)
    return record

@app.get("/get_id_correction/", description="This route is used for displaying ID correction requests")
async def get_all_id_corrections():
    return {"corrections": id_corrections}

# Run the app on port 8001
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
