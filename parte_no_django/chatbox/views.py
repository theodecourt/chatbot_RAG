from django.shortcuts import render, redirect
from .models import Chatbox

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

def apagar_banco(request):
    Chatbox.objects.all().delete()  # Deleta todos os registros
    return redirect('index')  # Redireciona para a página inicial
