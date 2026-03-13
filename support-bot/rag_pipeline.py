from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama  # for local LLaMA 3.3
from langchain_openai import ChatOpenAI
import json

def load_vectordb():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

def get_repair_instructions(fault_description: str, use_mock: bool = True) -> dict:
    """
    Given a fault description, retrieve repair steps from vector DB.
    use_mock=True: returns retrieved context without LLM (for demo)
    use_mock=False: uses LLaMA 3.3 via Ollama
    """
    vectordb = load_vectordb()
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    
    # Retrieve relevant chunks
    docs = retriever.get_relevant_documents(fault_description)
    context = "\n\n".join([d.page_content for d in docs])
    
    if use_mock:
        # Return retrieved context directly (no LLM needed for demo)
        return {
            "fault": fault_description,
            "retrieved_context": context,
            "repair_instructions": context,
            "source": "FAISS retrieval (mock mode)"
        }
    else:
        # Real LLaMA 3.3 via Ollama (run: ollama pull llama3.3)
        llm = Ollama(model="llama3.3")
        
        prompt = f"""You are a technical support engineer for Limi AI smart modules.
        
Using ONLY the following technical manual excerpts, provide specific repair instructions:

{context}

Fault reported: {fault_description}

Provide:
1. Likely fault code
2. Step-by-step repair instructions
3. Required parts/tools
4. Estimated repair time
"""
        response = llm(prompt)
        
        return {
            "fault": fault_description,
            "retrieved_context": context,
            "repair_instructions": response,
            "source": "LLaMA 3.3 + FAISS RAG"
        }

if __name__ == "__main__":
    result = get_repair_instructions(
        "Module overheating - internal temp 72°C, cooling fan noise detected",
        use_mock=True
    )
    print("=== RAG Result ===")
    print(result["repair_instructions"][:500])