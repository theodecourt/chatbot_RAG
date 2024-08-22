from django.shortcuts import render, redirect
from .models import Chatbox
import chromadb
from openai import OpenAI
import os

def index(request):
    if request.method == 'POST':
        pergunta = request.POST.get('pergunta')
        resposta = request.POST.get('resposta')

        if pergunta and resposta:
            # Cria uma nova instância de Chatbox e salva no banco de dados
            novo_chatbox = Chatbox(pergunta=pergunta, resposta=resposta)
            novo_chatbox.save()
            return redirect('index')
        else:
            # Se pergunta ou resposta estiverem vazios, renderize a página com uma mensagem de erro
            all_chats = Chatbox.objects.all()
            return render(request, 'chatbox/index.html', {'chats': all_chats, 'error': 'Por favor, preencha ambos os campos.'})
    
    # Este bloco será executado para o método GET
    all_chats = Chatbox.objects.all()
    return render(request, 'chatbox/index.html', {'chats': all_chats})

# --------------------------------------------- RAG BOT -------------------------------------------------------------------------------
# Inicialização do OpenAI e ChromaDB
openai_client = OpenAI(api_key="sk-HDhkci4_AuehZ5v1qw_7dUwLT6kjHurxqvT_dlEZGGT3BlbkFJEOcdwBRCMRnZquK5F9rgOWQhUPxRCo1a34nVJCLNAA")

chromadb_path = "./chatbox/data_politico/chroma_storage"  # Caminho para o ChromaDB
chroma_client = chromadb.PersistentClient(path=chromadb_path)
collection = chroma_client.get_collection("my_collection")

# Template para as respostas do chatbot
prompt_template = """Você é um assistente de IA que responde as dúvidas dos usuários com bases nos documentos abaixo.
Os documentos abaixo apresentam as fontes atualizadas e devem ser consideradas como verdade.
Cite a fonte quando fornecer a informação. 
Documentos:
{documents}
"""

def consulta_gpt(request):
    if request.method == 'POST':
        question = request.POST.get('pergunta')

        print(f"Usuario: {question}")

        # Buscar documentos relevantes no ChromaDB
        relevant_documents = search_document(question)
        print(f"Documentos Retornados: {relevant_documents}")

        documents_str = format_search_result(relevant_documents)

        # Atualizar o prompt com os documentos encontrados
        prompt = prompt_template.format(documents=documents_str)

        try:
            answer = execute_llm(prompt)
        except Exception as e:
            print(f"Erro ao gerar resposta: {e}")
            return render(request, 'chatbox/index.html', {'chats': Chatbox.objects.all(), 'error': 'Erro ao gerar a resposta.'})

        print(f"Chatbot: {answer}")
        novo_chatbox = Chatbox(pergunta=question, resposta=answer)
        novo_chatbox.save()
        return redirect('index')  # Redireciona para a página inicial
    
    # Este bloco será executado para o método GET
    all_chats = Chatbox.objects.all()
    return render(request, 'chatbox/index.html', {'chats': all_chats})

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
def execute_llm(prompt):
    chat_completion = openai_client.chat.completions.create(
        messages=[{"role": "system", "content": prompt}],
        model="gpt-3.5-turbo",
        max_tokens=400,
        temperature=0
    )
    return chat_completion.choices[0].message.content

# --------------------------------------------- RAG BOT -------------------------------------------------------------------------------


def apagar_banco(request):
    Chatbox.objects.all().delete()  # Deleta todos os registros
    return redirect('index')  # Redireciona para a página inicial
