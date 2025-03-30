from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import List, Dict, Any

# Initialize the embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

# Function to initialize Chroma vector database
def initialize_chroma(persist_directory: str = "./chroma_db"):
    """Initialize and return a Chroma vector database with the specified persistence directory."""
    try:
        # Try to load an existing database
        db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        print(f"Loaded existing Chroma database from {persist_directory}")
        return db
    except Exception as e:
        print(f"Error loading Chroma database: {e}")
        print("Creating new Chroma database")
        # Create a new database if loading fails
        db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        return db

# Function to add documents to Chroma
def add_documents_to_chroma(texts: List[str], metadatas: List[Dict[str, Any]] = None):
    """
    Add documents to the Chroma vector database.
    
    Args:
        texts: List of text strings to add to the database
        metadatas: Optional list of metadata dictionaries corresponding to each text
    """
    db = initialize_chroma()
    
    # If no metadata is provided, create empty dictionaries
    if metadatas is None:
        metadatas = [{} for _ in texts]
    
    # Add documents to the database
    db.add_texts(texts=texts, metadatas=metadatas)
    
    # Persist the database to disk
    db.persist()
    print(f"Added {len(texts)} documents to Chroma database")
    
    return db

# Example usage in your system
def setup_chroma_with_sample_data():
    """Example function to populate Chroma with sample data."""
    sample_texts = [
        "Our AI assistant chatbot was launched in 2020 to revolutionize how businesses interact with APIs and automate form-filling processes.",
        "The chatbot intelligently integrates with various API documentation, enabling seamless data extraction and form completion for users.",
        "Our AI assistant is available 24/7, helping businesses and individuals streamline workflows, reduce manual entry, and improve efficiency.",
        "The chatbot understands API structures, extracts relevant data fields, and dynamically builds conversational form-filling experiences tailored to user needs.",
        "Trusted by organizations worldwide, our AI assistant is designed to simplify API interactions and enhance productivity across industries."
    ]
    
    sample_metadata = [
        {"category": "company_info", "source": "about_page"},
        {"category": "support", "source": "help_center"},
        {"category": "policy", "source": "terms_page"},
        {"category": "product", "source": "product_page", "product_id": "X001"},
        {"category": "company_info", "source": "contact_page"}
    ]
    
    add_documents_to_chroma(sample_texts, sample_metadata)