# Import libraries
import sys
sys.path.append(".")
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from .config import OPENAI_API_KEY, CHAT_MODEL_NAME
from typing import List, Dict, Tuple, Optional


# Memory class to store and manage the chat history
class Memory:
    def __init__(self, max_messages_count=10):
        self._memory = []
        self.max_messages_count = max_messages_count
    def update_memory(self, human_msg: str, ai_msg: str):
        self._memory.append(
            {"role": "user", "content": human_msg}
        )
        self._memory.append(
            {"role": "assistant", "content": ai_msg}
        )

    def reset_memory(self):
        self._memory = []

    @property
    def history(self) -> List[Dict[str, str]]:
        return self._memory[-self.max_messages_count:]
    
    

# Main chatbot class
class ChatBot:
    def __init__(self):
        # Initialize OpenAI chat model
        self.chat_model = ChatOpenAI(
            model_name= CHAT_MODEL_NAME,
            api_key=OPENAI_API_KEY
        )
        self._context = None
        self._sources = None
        self.memory = Memory()

        # System prompt
        self.system_prompt = (
            "You are an AI assistant engaged in a conversation with a user. "
            "You will be given context extracted from user-provided documents. "
            "Your answers must be based **only** on this context—do not use outside knowledge or make assumptions. "
            "Cite or refer to specific parts of the context whenever relevant to support your answers. "
            "If the context does not contain enough information to answer the user's question, clearly state that. "
            "LANGUAGE RULE: By default, always respond in English unless the user explicitly writes in another language. "
            "If the user writes in a different language, respond in that same language. "
            "If the user's language is unclear, default to English."
        )

    def retrieve_context_from_db(self, query: str, vector_db) -> None:
        """
        Retrieve relevant context from the vector database for the given query.
        
        Args:
            query (str): The user's query
            vector_db: The vector database instance
        """
        self._context, self._sources = vector_db.retrieve_context(query)

    def remove_context(self) -> None:
        """
        Remove the current context and sources from the chatbot.
        """
        self._context = None
        self._sources = None

    def infer(self, message: str, history: Optional[List[Dict[str, str]]] = None) -> Tuple[str, List[Dict[str, str]]]:
        """
        Generate a response using OpenAI's API.

        Parameters:
            message (str): User input
            history (List[Dict[str, str]], optional): Chat history in format [{"role": "user/assistant", "content": "message"}]

        Returns:
            Tuple[str, List[Dict[str, str]]]: The model's response and sources used
        """
        # Prepare messages
        messages = [SystemMessage(content=self.system_prompt)]
        
        # Add context if available
        if self._context:
            context_message = (
                "Below is some context extracted from documents. Use this context to answer the question. "
                "If the context isn't directly related to the query or the information provided is not enough, "
                "please indicate this explicitly.\n\n"
                f"Context:\n{self._context}"
            )
            messages.append(HumanMessage(content=context_message))
            messages.append(SystemMessage(content="I understand the context. Please proceed with your question."))

        # Add chat history if available
        if history:
            for msg in history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(SystemMessage(content=msg["content"]))

        # Add current message
        messages.append(HumanMessage(content=message))

        # Get response from OpenAI
        response = self.chat_model.invoke(messages)
        
        # Return response and sources
        return response.content, self._sources if self._sources else []

if __name__=="__main__":
    cb = ChatBot()
    cb.infer("Hello")