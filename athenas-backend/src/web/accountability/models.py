# -*- coding:utf-8 -*-

from django.db import models


class DocumentCache(models.Model):

    class Meta:
        managed = False
        db_table = "document_cache_view"

    protocol_number = models.CharField(max_length=20)  # número do protocolo
    protocol_date = models.DateTimeField()  # data e hora de protocolo
    last_move_date = models.DateTimeField()  # data da última movimentação
    process_number = models.CharField(
        max_length=50, default="N/A"
    )  # número do processo (e-ext, diarias). Pode não ter processo associado.
    type = models.CharField(
        max_length=50
    )  # tipo do documento (memorando, ofício, diárias)
    id_type = models.IntegerField()
    id_source = models.IntegerField()
    source = models.CharField(max_length=120)  # origem do documento
    subject = models.CharField(max_length=200)  # assunto do documento
    protected = models.BooleanField(
        default=True
    )  # tipo de acesso (publico, privado, sigiloso).
    access_level = models.CharField(max_length=50)  # nível de sigilosidade
