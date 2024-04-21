from flask import Flask, render_template, request, jsonify
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import google.generativeai as genai
import os
import boto3
from googletrans import Translator
from langdetect import detect
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from cloudpathlib import CloudPath

load_dotenv()
os.getenv("GOOGLE_API_KEY")

google_key = 'AIzaSyA0e2ZFuHPlXhrQeKI7Lo0mt7GU07V29Pg'
genai.configure(api_key=os.getenv(google_key))

cp = CloudPath("s3://gueedodb/data/English/")
cp.download_to(os.getcwd() + "/data/")

def translate_german_to_english(text):
    try:
        translate = boto3.client('translate', region_name='us-east-1')
        response = translate.translate_text(
            Text=text,
            SourceLanguageCode='auto',
            TargetLanguageCode='en'
        )
        translated_text = response['TranslatedText']
        return translated_text
    except Exception as e:
        print(f"Translation error: {e}")

def translate_english_to_german(text):
    try:
        translate = boto3.client('translate', region_name='us-east-1')
        response = translate.translate_text(
            Text=text,
            SourceLanguageCode='auto',
            TargetLanguageCode='de'
        )
        translated_text = response['TranslatedText']
        return translated_text
    except Exception as e:
        print(f"Translation error: {e}")

def is_german(text):
    try:
        language = detect(text)
        if language == "de":
            return True
        else:
            return False
    except:
        return False

def get_pdf_text(data_path):
    pdf_files = [os.path.join(data_path, file) for file in os.listdir(data_path) if file.endswith('.pdf')]
    all_texts = ''
    for pdf_file in pdf_files:
        with open(pdf_file, 'rb') as f:
            reader = PdfReader(f)
            text = ''.join(page.extract_text() for page in reader.pages)
            all_texts += text
    return all_texts

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=google_key)
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

    model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3, google_api_key=google_key)

    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain

def user_input(user_question):
    lang = ''
    if is_german(user_question):
        user_question = translate_german_to_english(user_question)
        lang = 'de'

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=google_key)
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)

    reply = response["output_text"]
    
    if lang == 'de':
        reply = translate_english_to_german(reply)
    #print(reply ,"answer")
    
    return reply

app = Flask(__name__)

@app.route('/')
def index():
    pdf_docs = os.getcwd() + "/data/"
    raw_text = get_pdf_text(pdf_docs)
    text_chunks = get_text_chunks(raw_text)
    get_vector_store(text_chunks)
    return render_template('index.html')

@app.route('/submit_question', methods=['POST'])
def submit_question():
    #print("Raw request data:", request.data)
    data = request.get_json()
    #print("Parsed JSON data:", data)
    question = data.get('question')
    print(question ,"question")
    try:
        response = user_input(question)
    except:
        response = "Unable to find the answer in HR context/data, Please ask question related to the HR Policy"
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
