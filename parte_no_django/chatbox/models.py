from django.db import models


class Chatbox(models.Model):
    pergunta = models.TextField()
    resposta = models.TextField()

    def __str__(self):
        return f"{self.id}. {self.pergunta}"