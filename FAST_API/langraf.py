#pip install langchain langraph pypdf langchain-openai faiss-cpu
import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain.chains import RetrievalQA
from langraph.graph import StateGraph,END
from typing import TypedDict,List
import operator
from typing_extensions import Annotated
os.environ["OPENAI_API_KEY"] = "sk-YOUR-KEY-HERE"

def load_documents(file_path: list[str]):
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.txt'):
        loader = TextLoader(file_path)
    else:
        raise ValueError("Unsupported file format")
    return loader.load()

def chunk_documents(documents, chunk_size=1000, chunk_overlap=200):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks=text_splitter.split_documents(documents) 
    return chunks

def create_embeddings(chunks):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore

def test_retrieval_qa(vectorstore, query,k=3):
    relevant_docs = vectorstore.similarity_search(query, k=k)
    print(f"Retrieved {len(relevant_docs)} documents.")
    for i, doc in enumerate(relevant_docs):
        print(f"Document {i+1}:\n{doc.page_content}\n")
        print(f'Metadata: {doc.metadata}\n')
    return relevant_docs

class RAGState(TypedDict):
    query: str
    relevant_docs: Annotated[List[str], operator.add]
    answer: str
def retrieve_node(state: RAGState) -> RAGState:
    vectorstore = state['vectorstore']
    query = state['query']
    relevant_docs = test_retrieval_qa(vectorstore, query)
    state['relevant_docs'] = [doc.page_content for doc in relevant_docs]
    return state

llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
prompt_template = "You are a helpful assistant. Use the following pieces of context to answer the question at the end."

def generate_answer(state: RAGState) -> RAGState:
    relevant_docs = "\n\n".join(state['relevant_docs'])
    query = state['query']
    prompt = ChatPromptTemplate.from_template(f"{prompt_template}\n\nContext:\n{relevant_docs}\n\nQuestion: {query}\nAnswer:")
    answer = llm.predict(prompt.format_messages({}))
    state['answer'] = answer
    return state

def build_rag_graph(vectorstore) -> StateGraph[RAGState]:
    graph = StateGraph[RAGState]()
    graph.add_state('start', {'vectorstore': vectorstore, 'query': '', 'relevant_docs': [], 'answer': ''})
    graph.add_node('retrieve', retrieve_node)
    graph.add_node('generate', generate_answer)
    graph.add_edge('start', 'retrieve')
    graph.add_edge('retrieve', 'generate')
    graph.add_edge('generate', END)
    app = graph.compile()
    return app

def complete_rag_process(file_path: str, query: str):
    documents = load_documents(file_path)
    chunks = chunk_documents(documents)
    vectorstore = create_embeddings(chunks)
    rag_graph = build_rag_graph(vectorstore)
    initial_state: RAGState = {'vectorstore': vectorstore, 'query': query, 'relevant_docs': [], 'answer': ''}
    final_state = rag_graph.run(initial_state)
    return final_state['answer']

def ask_question(file_path: str, question: str):
    answer = complete_rag_process(file_path, question)
    print(f"Answer: {answer}")
# Example usage:
# ask_question('sample.pdf', 'What is the main topic of the document?')