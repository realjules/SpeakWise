from fastapi.testclient import TestClient

from app import app

client = TestClient(app)

def test_get_conversations():
    response = client.get("/conversations/")
    assert response.status_code == 200, "Cannot Retrieve Conversations"

def test_ask_question():
    response = client.post("/chat/", json={"message":"i would like some information about school"})
    assert response.status_code == 200, "Cannot Respond to a question"

def test_request_form():
    response = client.post("/chat/", json={"message":"i would like to apply for a new national ID"})
    assert response.status_code ==200, "Cannot Respond to a form filling request"
    
    intent = response.json()["entities"]["intent"]
    assert intent == "fill_form", "Cannot recognise intent of fill_form"

def test_request_and_fill_form():
    response = client.post("/chat/", json={"message":"i would like to apply for a new national ID"})
    assert response.status_code ==200, "Cannot Respond to a form filling request"
    intent = response.json()["entities"]["intent"]
    assert intent == "fill_form", "Cannot recognise intent of fill_form"
    
    response = client.post("/chat/", json={"message": "the child identification is io23423"})
    assert response.status_code ==200, "Cannot Extract information from message"
    information = response.json()["entities"]["information"]
    assert information["childID"] == "io23423", "Cannot Extract child identification from the above message"

    response = client.post("/chat/", json={"message": "the child's biometric sector is Kicukiro"})
    assert response.status_code ==200, "Cannot Extract information from message"
    information = response.json()["entities"]["information"]
    assert information["childID"] == "io23423", "Did not save previous extracted information"
    assert information["biometricSector"] == "Kicukiro", "Cannot Extract child biometric sector"
    
