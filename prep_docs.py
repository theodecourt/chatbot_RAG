import PyPDF2
from openai import OpenAI
import chromadb
import uuid
import os
from dotenv import load_dotenv

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv(verbose=True, override=True)


# Obter a chave da API a partir do .env
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Inicialização do OpenAI e ChromaDB
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) 

CHUNK_SIZE = 1000
OFFSET = 200

chromadb_path = "./data_politico/chroma_storage"  # Configura o caminho para o ChromaDB
chroma_client = chromadb.PersistentClient(path=chromadb_path)
collection = chroma_client.get_or_create_collection(name="my_collection")



def get_document(document_path):
    """Ler um documento PDF e retornar o texto em string"""
    with open(document_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        document_text = ""
        for page in reader.pages:
            document_text += page.extract_text()
        return document_text

def split_document(document_text):
    """Dividir um documento em uma lista de strings"""
    documents = []
    for i in range(0, len(document_text), CHUNK_SIZE):
        start = i
        end = i + CHUNK_SIZE
        if start != 0:
            start -= OFFSET
            end -= OFFSET
        documents.append(document_text[start:end])
    return documents

def get_embedding(text):
    """Transformar um texto em um vetor usando o modelo de embedding"""
    embedding = openai_client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return embedding.data[0].embedding

def prepare_documents(documents, document_name):
    """Preparar documentos para o banco de dados vetorial, gerando embedding e metadados"""
    embeddings = []
    metadatas = []
    for i, doc in enumerate(documents):
        embeddings.append(get_embedding(doc))
        metadatas.append({"source": document_name, "partition": i})
    return embeddings, metadatas

def create_ids(documents):
    """Criar uma lista de IDs para os documentos"""
    return [str(uuid.uuid4()) for _ in documents]

def insert_data(documents, embeddings, metadatas, ids):
    """Inserir dados na coleção do ChromaDB"""
    collection.add(
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print(f"Dados inseridos com sucesso! {len(documents)} fragmentos adicionados.")

def run():
    print("Preparando documentos...")
    path = 'data_politico/adriana_ventura.pdf'

    # Verifica se o arquivo PDF existe
    if not os.path.exists(path):
        print(f"Arquivo {path} não encontrado!")
        return

    # Ler o documento PDF
    document = get_document(path)
    document_chunks = split_document(document)
    
    # Preparar embeddings e metadados
    document_embeddings, document_metadatas = prepare_documents(document_chunks, 'adriana_ventura.pdf')
    
    # Criar IDs para os documentos
    ids = create_ids(document_chunks)
    
    # Inserir dados no banco de dados vetorial
    insert_data(document_chunks, document_embeddings, document_metadatas, ids)
        
if __name__ == "__main__":
    run()
