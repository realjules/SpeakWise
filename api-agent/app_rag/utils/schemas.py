from pydantic import BaseModel

# Define conversation data schema
class ConversationData(BaseModel):
    message: str
