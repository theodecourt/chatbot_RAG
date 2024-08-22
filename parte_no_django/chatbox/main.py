import chromadb
from openai import OpenAI
import os

# Inicialização do OpenAI e ChromaDB
openai_client = OpenAI(api_key="sk-HDhkci4_AuehZ5v1qw_7dUwLT6kjHurxqvT_dlEZGGT3BlbkFJEOcdwBRCMRnZquK5F9rgOWQhUPxRCo1a34nVJCLNAA")

chromadb_path = "./data_politico/chroma_storage"  # Caminho para o ChromaDB
chroma_client = chromadb.PersistentClient(path=chromadb_path)
collection = chroma_client.get_collection("my_collection")

# Template para as respostas do chatbot
prompt_template = """Você é um assistente de IA que responde as dúvidas dos usuários com bases nos documentos abaixo.
Os documentos abaixo apresentam as fontes atualizadas e devem ser consideradas como verdade.
Cite a fonte quando fornecer a informação. 
Documentos:
{documents}
"""

# Função para transformar texto em vetores usando o modelo de embedding
def get_embedding(text):
    embedding = openai_client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return embedding.data[0].embedding

# Função para buscar documentos relevantes no ChromaDB
def search_document(question):
    query_embedding = get_embedding(question)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )
    return results

# Função para formatar o resultado da pesquisa em uma string utilizável no prompt
def format_search_result(relevant_documents):
    formatted_list = []
    for i, doc in enumerate(relevant_documents["documents"][0]):
        formatted_list.append("[{}]: {}".format(relevant_documents["metadatas"][0][i]["source"], doc))
    return "\n".join(formatted_list)

# Função para gerar a resposta do modelo levando em consideração o histórico de mensagens
def execute_llm(messages):
    chat_completion = openai_client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
        max_tokens=400,
        temperature=0
    )
    return chat_completion.choices[0].message.content

# Função principal do chatbot
def run_chatbot():
    conversation_history = []  # Histórico de mensagens (usuário e assistente)
    
    print("Chatbot iniciado. Digite 'sair' para encerrar.")
    
    while True:
        question = input("Você: ")
        
        if question.lower() == "sair":
            break
        
        # Buscar documentos relevantes no ChromaDB
        relevant_documents = search_document(question)
        print(f"Documentos Retornados: {relevant_documents}")
        documents_str = format_search_result(relevant_documents)
        
        # Atualizar o prompt com os documentos encontrados
        prompt = prompt_template.format(documents=documents_str)
        
        # Adicionar o prompt de sistema ao histórico de mensagens
        conversation_history.append({"role": "system", "content": prompt})
        
        # Adicionar a pergunta do usuário ao histórico
        conversation_history.append({"role": "user", "content": question})
        
        # Gerar a resposta do ChatGPT
        answer = execute_llm(conversation_history)
        
        # Adicionar a resposta do chatbot ao histórico
        conversation_history.append({"role": "assistant", "content": answer})
        
        # Exibir a resposta ao usuário
        print(f"Chatbot: {answer}")

if __name__ == "__main__":
    run_chatbot()
