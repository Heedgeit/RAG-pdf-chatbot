from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain.schema.document import Document
import chromadb
from chromadb.utils import embedding_functions
import ollama

path = "database"

def load_docs() :
    loader = PyPDFDirectoryLoader(path)
    return loader.load()

docs = load_docs()

def split(documents: list[Document]) :
    splitter = RecursiveCharacterTextSplitter(chunk_size= 1000,
                                                   chunk_overlap= 200,
                                                   is_separator_regex= False)
    return splitter.split_documents(documents)


chunks = split(docs)

last_pid = None
chunk_id = []
c_id = 0 

for c in chunks :
    source = c.metadata.get("source")
    page = c.metadata.get("page")

    if page == last_pid :
        c_id += 1
        chunk_id.append(f'{source}:{page}:{c_id}')
    else :
        c_id = 0
        chunk_id.append(f'{source}:{page}:{c_id}')
        last_pid = page

base = chromadb.PersistentClient("medical")


ollama_ef = embedding_functions.OllamaEmbeddingFunction(
    model_name="nomic-embed-text:v1.5",
    url="http://localhost:11434" 
)


embed = []

doc = []

for i in chunks :
    res = ollama.embeddings(model= 'nomic-embed-text:v1.5', prompt=str(i))
    embed.append(res['embedding'])
    doc.append(i)

col = base.get_or_create_collection("aids", embedding_function=ollama_ef)

col.upsert(
    ids= chunk_id,
    embeddings= embed,
    documents= [str(i) for i in doc]
)

