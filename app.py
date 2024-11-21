import streamlit as st
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import os
import pickle
from pypdf import PdfReader

# Configuration Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_google_drive_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('drive', 'v3', credentials=creds)

@st.cache_resource
def get_vectorstore():
    # Créer un dossier pour ChromaDB s'il n'existe pas
    if not os.path.exists("chroma_db"):
        os.makedirs("chroma_db")
    
    service = get_google_drive_service()
    folder_id = '1rsEioMwqcDsm2Gui15H0IDauHmSZt2cM'
    
    results = service.files().list(
        q=f"'{folder_id}' in parents and mimeType='application/pdf'",
        fields="files(id, name)"
    ).execute()
    
    texts = []
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    for file in results.get('files', []):
        request = service.files().get_media(fileId=file['id'])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        fh.seek(0)
        pdf_reader = PdfReader(fh)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        texts.extend(text_splitter.split_text(text))
    
    embeddings = OllamaEmbeddings(model="llama2")
    # Spécifier le chemin pour la persistance
    return Chroma.from_texts(
        texts, 
        embeddings,
        persist_directory="chroma_db"
    )

def get_chat_response(query, chat_history, use_rag=True, temperature=0.7):
    llm = Ollama(model="llama2", temperature=temperature)
    
    if use_rag:
        vectorstore = get_vectorstore()
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(),
            return_source_documents=True
        )
        response = qa_chain({"question": query, "chat_history": chat_history})
        return response['answer']
    else:
        response = llm.invoke(query)
        return response

def main():
    st.title("ChatBot RAG vs Non-RAG")
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    use_rag = st.sidebar.checkbox("Utiliser RAG", value=True)
    temperature = st.sidebar.slider("Température", 0.0, 1.0, 0.7)
    
    with st.spinner("Chargement des documents..."):
        if use_rag:
            get_vectorstore()
    
    query = st.text_input("Votre question:")
    
    if st.button("Envoyer"):
        with st.spinner("Génération de la réponse..."):
            response = get_chat_response(
                query,
                st.session_state.chat_history,
                use_rag,
                temperature
            )
            
            st.session_state.chat_history.append((query, response))
            
            for q, r in st.session_state.chat_history:
                st.write(f"Q: {q}")
                st.write(f"R: {r}")
                st.write("---")

if __name__ == "__main__":
    main() 