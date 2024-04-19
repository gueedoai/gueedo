import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()
os.getenv("GOOGLE_API_KEY")

google_key = 'AIzaSyA0e2ZFuHPlXhrQeKI7Lo0mt7GU07V29Pg'
genai.configure(api_key=os.getenv(google_key))

def get_pdf_text(data_path):
    pdf_files = [os.path.join(data_path, file) for file in os.listdir(data_path) if file.endswith('.pdf')]
    all_texts = ''
    for pdf_file in pdf_files:
        with open(pdf_file, 'rb') as f:
            reader = PdfReader(f)
            text = ''.join(page.extract_text() for page in reader.pages)
            all_texts += text
    return  all_texts

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001",google_api_key=google_key)
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def get_conversational_chain():

    prompt_template = """
    Answer the question as detailed as possible from the provided context, make sure to provide all the details, if the answer is not in
    provided context just say, "answer is not available in the context", don't provide the wrong answer\n\n
    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro",temperature=0.3,google_api_key=google_key)

    prompt = PromptTemplate(template = prompt_template, input_variables = ["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001",google_api_key=google_key)
    
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    
    response = chain(
        {"input_documents":docs, "question": user_question}
        , return_only_outputs=True)

    #print(response)
    st.write("Reply: ", response["output_text"])

def main():
    
    pdf_docs = 'C:/Users/Administrator/Documents/data/'
    raw_text = get_pdf_text(pdf_docs)
    text_chunks = get_text_chunks(raw_text)
    get_vector_store(text_chunks)

    st.set_page_config("AI Loves HR")
    st.header("AI Chatbot for HR Related Queries")
    st.markdown("This AI chatbot is designed to assist with human resources (HR) related queries. It is programmed to provide responses and support for various topics and inquiries pertaining to HR functions, policies, procedures, and employee-related matters. Users can interact with the chatbot to seek information, guidance, and solutions regarding recruitment, onboarding, employee benefits, performance management, HR policies, and other relevant areas within the HR domain. The chatbot aims to streamline HR processes, enhance user experience, and provide timely assistance to employees and HR professionals alike.")

    user_question = st.text_input("Ask a Question")

    
    if user_question:
        user_input(user_question)


if __name__ == "__main__":
    main()