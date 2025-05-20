from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from .config import OPENAI_API_KEY, RAG_DECISION_MODEL_NAME, SUMMARY_MODEL_NAME
from typing import Optional

def summarize_document(text: str) -> str:
    """
    Summarizes the given text using OpenAI's API.
    
    Args:
        text (str): The text to summarize
        
    Returns:
        str: The summary
    """
    # Initialize OpenAI chat model
    chat_model = ChatOpenAI(
        model_name=SUMMARY_MODEL_NAME,
        api_key=OPENAI_API_KEY
    )
    
    # System prompt for summarization
    system_prompt = (
        "You are an AI assistant that summarizes documents."
        "You will be given a document and you need to summarize it in a few sentences."
        "You must be very concise and to the point. "
        "Extract the inherent information from the document and summarize it."
        "Watever the language the document is in, summarize it in English."
    )
    
    # Prepare messages
    messages = [SystemMessage(content=system_prompt)]
    messages.append(SystemMessage(content=text))
    
    # Get response from OpenAI
    response = chat_model.invoke(messages)
    
    return response.content

def should_use_rag(message: str, summaries: str, model_name: Optional[str] = None) -> bool:
    """
    Determine if a message should be processed using RAG by comparing it against document summaries.
    
    Args:
        message (str): The user's message
        summaries (str): Concatenated summaries of all documents
        model_name (str, optional): Name of the model to use. If None, uses default from config.
        
    Returns:
        bool: True if the message should use RAG, False otherwise
    """
    try:
        print("\n=== RAG Decision Check Debug ===")
        print(f"Using model: {model_name or RAG_DECISION_MODEL_NAME}")
        print(f"\nUser message: {message}")
        print(f"\nAvailable document summaries:\n{summaries}")
        
        if not summaries:
            print("No documents available, skipping RAG")
            return False  # No documents available, can't do RAG
            
        # Initialize OpenAI chat model with optional custom model
        chat_model = ChatOpenAI(
            model_name=model_name or RAG_DECISION_MODEL_NAME,
            api_key=OPENAI_API_KEY
        )
        
        # System prompt for RAG decision
        system_prompt = (
            "You are an AI assistant that determines if a user's question is related to the content of provided documents. "
            "You will be given a user's question and summaries of available documents. "
            "Your task is to determine if the question is likely to be answered using the document content. "
            "Consider the following:\n"
            "1. Is the question about topics covered in the documents?\n"
            "2. Would the documents contain information needed to answer the question?\n"
            "3. Is the question general knowledge or specific to the document content?\n"
            "4. Is the question asking for a summary or overview of the available documents?\n\n"
            "Respond with a confidence score (0-100) indicating how likely it is that the question "
            "can be answered using the document content. "
            "If the score is above 70, the question is RAG-worthy.\n\n"
            "Example responses:\n"
            "85 - The question is clearly about topics covered in the documents\n"
            "45 - The question might be partially related but likely needs general knowledge\n"
            "20 - The question appears to be about general knowledge or unrelated topics"
        )
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User question: {message}\n\nDocument summaries:\n{summaries}")
        ]
        
        response = chat_model.invoke(messages)
        content = response.content.lower()
        print(f"\nModel response: {response.content}")
        
        # Quick check for summary requests
        if any(phrase in message.lower() for phrase in ["summary", "summarize", "summarise", "overview"]):
            return True
        
        # Try to extract confidence score
        try:
            # Look for a number between 0-100 in the response
            import re
            score_match = re.search(r'\b([0-9]{1,2}|100)\b', content)
            if score_match:
                confidence = int(score_match.group(1))
                print(f"Extracted confidence score: {confidence}")
                print(f"Decision: {'Use RAG' if confidence > 70 else 'Skip RAG'}")
                return confidence > 70
        except (ValueError, AttributeError) as e:
            print(f"Error extracting confidence score: {str(e)}")
            print("Falling back to phrase matching")
        
        # Fallback to phrase matching if confidence score parsing fails
        pos_decision_phrases = ["true", "yes", "correct", "rag worthy", "high confidence"]
        neg_decision_phrases = ["false", "no", "incorrect", "not rag worthy", "low confidence"]
        
        decision = any(phrase in content for phrase in pos_decision_phrases)
        print(f"Phrase matching decision: {'Use RAG' if decision else 'Skip RAG'}")
        print("=== End RAG Decision Check ===\n")
        
        return decision
        
    except Exception as e:
        print(f"Error in RAG decision check: {str(e)}")
        print("Defaulting to use RAG due to error")
        return True 