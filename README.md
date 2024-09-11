# Como rodar o projeto Django

Siga os passos abaixo para rodar o projeto localmente:

## 1. Ative o ambiente virtual
- No Linux/macOS:
  ```bash
  source venv/bin/activate
No Windows:
bash
Copy code
venv\Scripts\activate
2. Instale as dependências
Caso ainda não tenha instalado, use o arquivo requirements.txt para instalar as dependências do projeto:

bash
Copy code
pip install -r requirements.txt
3. Realize as migrações do banco de dados
Garanta que o banco de dados esteja atualizado com os modelos:

bash
Copy code
python manage.py migrate
4. Crie um superusuário (Opcional)
Para acessar o painel administrativo do Django, crie um superusuário:

bash
Copy code
python manage.py createsuperuser
5. Inicie o servidor de desenvolvimento
Para rodar o servidor de desenvolvimento, utilize o comando:

bash
Copy code
python manage.py runserver
6. Acesse o projeto
Abra o navegador e vá para http://127.0.0.1:8000 para visualizar o projeto rodando.