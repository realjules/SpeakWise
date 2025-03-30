from pydantic import create_model, BaseModel, Field
from typing import Optional
from langchain_groq import ChatGroq  # Modify the import according to your actual Groq API implementation
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .chroma_utils import *

groq = ChatGroq(model="llama3-70b-8192", groq_api_key="<GROQ API KEY>")


# Helper function to call Groq LLM for chatbot responses
def call_groq_llm(message: str) -> str:
    prompt = message
    generated_answer = groq.invoke(prompt)  # Using the Groq LLM to generate a response
    return generated_answer

def generate_dynamic_model(fields:dict):
    DynamicFieldsModel = create_model("DynamicModel", **{key: (Optional[str], None) for key in fields.keys()})
    return DynamicFieldsModel(**fields)

# Function to classify intents
def classify_intent(message: str) -> str:
    # Use Groq's LLM to classify the intent
    prompt = f"Classify the intent of the following message: '{message}'. The possible intents are: 'ask_question', 'fill_form', 'stop_form', or 'unknown'."
    
    # Call Groq's LLM to classify the intent
    llm_response = groq.invoke(prompt)
    
    # Extract the intent from the LLM's response
    if "ask_question" in llm_response.content.lower():
        return "ask_question"
    elif "fill_form" in llm_response.content.lower():
        return "fill_form"
    elif "stop_form" in llm_response.content.lower():
        return "stop_form"
    else:
        return "unknown"

def classify_form(message: str, paths_info: list):
    paths_and_descriptions = {}
    paths_and_fields = {}
    paths = []
    for path in paths_info:
        paths_and_descriptions[path["path"]] = path["description"]
        paths_and_fields[path["path"]] = {"fields":path["fields"], "required_fields": path["required_fields"]}
        paths.append(path["path"])
    paths_str = ", ".join(item for item in paths)
    prompt = (
        f"Classify the form intended for the following message: '{message}' and return only the path for the form. "
        f"The possible forms and their descriptions are: {paths_and_descriptions}. "
        f"I want responses only in this format: {paths} and 'unknown'."
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert classification algorithm. "
                "Classify the form intended for the following message and return only the path for the form. "
                "The possible forms and their descriptions are: {paths_and_descriptions}. "
                "I want responses only in this format: {paths} and 'unknown'.",
            ),
            ("human", "{message}"),
        ]
    )

    class Classifier(BaseModel):
        intent: str = Field(..., enum=paths)

    # llm_response = prompt | groq.invoke(prompt).content[1:-1]
    runnable = prompt | groq.with_structured_output(schema=Classifier)
    llm_response = runnable.invoke({"message":message,"paths_and_descriptions":paths_and_descriptions, "paths":paths_str}).intent
    try:
        fields = paths_and_fields[llm_response]
        description = paths_and_descriptions[llm_response]
    except:
        fields = {} 
        description = ""
    return llm_response, fields, description

# def extract_field(message:str, field:str):
#     prompt = f"Extract the {field} from the following message: {message}"
#     llm_response = groq.invoke(prompt).content
#     return llm_response

def extract_fields(message:str, fields:dict):
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert extraction algorithm. "
                "Only extract relevant information from the message. "
                "If you do not know the value of an attribute asked to extract, "
                "return null for the attribute's value.",
            ),
            ("human", "{message}"),
        ]
    )
    DynamicFieldsModel = create_model("DynamicModel", **{key: (Optional[str], None) for key in fields.keys()})
    runnable = prompt | groq.with_structured_output(schema=DynamicFieldsModel)
    response = dict(runnable.invoke({"message":message}))
    for key, value in fields.items():
        if response[key] is not None:
            continue
        if value is not None:
            response[key] = value
    return response


class ResponseFormat(BaseModel):
    response: str


def generate_field_request(route_description:str, field:str):
    prompt = f"Generate a question for asking for {field} for a route with the description '{route_description}'"
    llm_response = groq.with_structured_output(ResponseFormat).invoke(prompt).response
    return llm_response

def generate_fields_request(route_description: str, fields: dict):
    prompt = f"Generate a question for asking for the following fields: {fields} \nfor a route with the description '{route_description}'"
    llm_response = groq.invoke(prompt).content
    return llm_response

def generate_report(state):
    prompt = f"Generate a tabular report on the information collected in the following context: {state}"
    llm_response = groq.invoke(prompt).content
    return llm_response

# Function to retrieve answers from Chroma vector database
# def get_answer_from_chroma(question: str) -> str:
#     # Chroma interaction code goes here
#     # Replace the following line with the actual retrieval code
#     return f"Answer to '{question}' from Chroma."


# Function to retrieve answers from Chroma vector database
def get_answer_from_chroma(question: str, groq_model: ChatGroq=groq, k: int = 3) -> str:
    """
    Retrieve relevant documents from Chroma based on the question,
    then use Groq LLM to generate an answer based on those documents.
    
    Args:
        question: The user's question
        groq_model: Initialized Groq LLM model
        k: Number of documents to retrieve
        
    Returns:
        Generated answer based on retrieved documents
    """
    # Initialize the Chroma database
    db = initialize_chroma()
    
    # Retrieve the k most relevant documents
    docs = db.similarity_search(question, k=k)
    
    # Extract the content from the documents
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # Create a RAG prompt template
    rag_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that answers questions based on the provided context.
        If the answer cannot be found in the context, politely state that you don't have that information.
        Keep your answers concise and directly address the user's question."""),
        ("human", "Context:\n\n{context}\n\nQuestion: {question}")
    ])
    
    # Create the RAG chain
    rag_chain = (
        rag_prompt 
        | groq_model 
        | StrOutputParser()
    )
    
    # Execute the chain
    answer = rag_chain.invoke({
        "context": context,
        "question": question
    })
    
    return answer