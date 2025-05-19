import os
import sys

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, project_root)

from src.core import GalteaChat

def main():
    # Initialize the chat system
    chat = GalteaChat()

    # List current documents in the system
    print("\nCurrent documents in the system:")
    documents = chat.list_documents()
    print(documents)

    # Test document-specific query
    print("\nTesting VW service query:")
    response, sources = chat.process_message("¿Qué incluye el servicio de mantenimiento de los 30,000 km?")
    print(f"Response: {response}")
    print(f"Sources: {sources}")

    # Test another relevant query
    print("\nTesting DSG transmission query:")
    response, sources = chat.process_message("¿Cada cuánto se cambia el aceite de la transmisión DSG?")
    print(f"Response: {response}")
    print(f"Sources: {sources}")

    # Optional general query to ensure separation
    print("\nTesting general query (should not be related to VW):")
    response, sources = chat.process_message("¿Qué vacinas se necesitan para viajar a África?")
    print(f"Response: {response}")
    print(f"Sources: {sources}") # should be empty

if __name__ == "__main__":
    main()