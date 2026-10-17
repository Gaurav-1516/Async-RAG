import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_qdrant import QdrantVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# 1. Embeddings
embedding_model = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2",
    google_api_key=os.getenv("gemini_key")
)

# 2. Connect to existing collection (Fixed from from_documents)
vectorstore = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="doc_rag_collection",
    embedding=embedding_model,
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 3. Prompt setup
SYSTEM_PROMPT = """You are an expert document analysis assistant. Your role is to provide accurate, helpful, and contextually relevant answers based SOLELY on the provided document context.

Instructions:
1. Answer questions using ONLY the information from the provided context
2. If the answer is not in the context, say "I don't have enough information to answer this question based on the provided documents"
3. Provide clear, concise answers with specific references to the context when possible
4. Do not make up information or use external knowledge
5. If asked about document details, summarize the relevant sections

Current context date: 2026-10-17

Always respond in a helpful, professional tone."""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "Context from documents:\n{context}\n\nQuestion: {question}\n\nPlease provide a comprehensive answer based on the context above:")
])

# 4. LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-3.7-flash",
    google_api_key=os.getenv("gemini_key"),
    temperature=0.1,
)

# Helper function to format retrieved documents
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 5. LCEL Chain
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# # Example execution
# if __name__ == "__main__":
#     query = "What is the summary of the document?"
#     response = rag_chain.invoke(query)
#     print(response)

def process_query(query: str):
    response = rag_chain.invoke(query)
    return response

def process_file(file_path: str):
    if file_path.lower().endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        loader = TextLoader(file_path)
        
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(documents)
    
    vectorstore.add_documents(split_docs)
    
    try:
        os.remove(file_path)
    except Exception:
        pass
        
    return f"Successfully processed {len(split_docs)} chunks from {os.path.basename(file_path)}."