
import os
from dotenv import load_dotenv
load_dotenv()

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

def load_documents_from_folder(folder_path):
    docs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            loader = TextLoader(os.path.join(folder_path, filename), encoding="utf-8")
            docs.extend(loader.load())
    return docs

def create_vectorstore_from_docs(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    split_docs = splitter.split_documents(documents)
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(split_docs, embedding=embeddings)
    return vectorstore

def save_vectorstore(vectorstore, path="faiss_index"):
    vectorstore.save_local(path)

def load_vectorstore(path="faiss_index"):
    embeddings = OpenAIEmbeddings()
    return FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)

def build_rag_qa_chain(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    qa_chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model_name="gpt-3.5-turbo"),
        retriever=retriever
    )
    return qa_chain

def init_rag(folder_path):
    if os.path.exists("faiss_index"):
        print("📁 저장된 벡터 DB를 불러옵니다...")
        vectorstore = load_vectorstore()
    else:
        print("📄 처음 실행 중: 문서를 처리하고 저장합니다...")
        docs = load_documents_from_folder(folder_path)
        vectorstore = create_vectorstore_from_docs(docs)
        save_vectorstore(vectorstore)
        print("✅ 벡터 DB 저장 완료")

    return build_rag_qa_chain(vectorstore)

def ask_rag_question(chain, question):
    try:
        result = chain.invoke(question)
        return result["result"].strip()
    except Exception as e:
        print(f"⚠️ RAG 처리 오류: {e}")
        return None

def ask_gpt_fallback(messages):
    from openai import OpenAI
    from config.settings import OPENAI_API_KEY
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-0125:personal::BJ1er10k",
        messages=messages
    )
    return response.choices[0].message.content
