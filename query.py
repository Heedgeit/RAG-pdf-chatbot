from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain.schema.document import Document
import chromadb
from chromadb.utils import embedding_functions
import ollama
import time

import streamlit as st

def stream(text,delay:float=0.02) :
    for word in text.split('\n'):
        yield word + " "
        time.sleep(delay)

base = chromadb.PersistentClient("medical")

ollama_ef = embedding_functions.OllamaEmbeddingFunction(
    model_name="nomic-embed-text:v1.5",
    url="http://localhost:11434" 
)

col = base.get_collection("aids", embedding_function= ollama_ef)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if prompt := st.chat_input('What is up?'):
    with st.chat_message("User"):
        st.markdown(prompt)

    st.session_state.messages.append({"role":"user", "content": prompt})
    result = col.query(
        query_texts= [prompt],
        n_results= 3,
        include=["documents"]
    )
    with st.chat_message("assistant"):
        with st.spinner("Thinking"):
            mssg = st.empty()
            full_resp = ""
            data = result['documents']
            resp = ollama.generate(
                model='qwen3:1.7b',
                prompt = f'''You are a helpful assistant. Always respond in Nigerian English.
                Using your input {[i for i in data]}. Respond to the question: {prompt}, 
                give summarized explanations to it, in bullet points.
                ''',
                stream= True
                
            ) 

            def response_generator():
                for chunk in resp:
                    yield chunk["response"]  # Adjust key based on actual response format

            st.write_stream(response_generator())
            #response = resp['message']['content']
            for r in resp:
                
                #mssg.write_stream(r['response'])  # Collecting the streamed response
                full_resp += r['response']
            #mssg.markdown(full_resp)
                

            st.session_state.messages.append({"role":"assistant",
                                            "content": full_resp})
            
with st.sidebar :
    for i in st.session_state.messages :
        if i['role']=='user' :
            st.write(i['content'])