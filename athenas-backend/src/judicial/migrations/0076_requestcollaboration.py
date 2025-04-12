# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
from django.db.models import F
from judicial.models import WorkerReminder, LegalMoviment
import django.db.models.deletion


def up_update_data(apps, schema_editor):
    from engine.notification.models import Message
    from judicial.models import Tag

    print("\n create message...")
    message = Message(
        mid="EJUD_COLLABORATION",
        header="E-Ext: Pedido de Colaboração",
        message="Foi realizado um pedido de colaboração por %(location)s para o procedimento %(type_lawsuit)s %(cache_number)s",
    )
    message.save()

    print("update slugs tag system")
    for tag in Tag.objects.filter(tag_type=1):
        tag.title = tag.title.upper()
        tag.save()

    WorkerReminder.objects.filter(resolved=True).update(
        resolved_by=F("modified_by"), resolved_at=F("modified_at")
    )

    LegalMoviment.objects.filter(judicial_classification=True).update(
        collaborator_can_sign=True
    )


def down_fake(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0092_auto_20190617_1447"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("judicial", "0075_change_suspenddeadline"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="movementlog",
            options={"ordering": ("out_court_lawsuit", "sended_at")},
        ),
        migrations.AlterUniqueTogether(
            name="notifystack",
            unique_together=set([]),
        ),
        migrations.CreateModel(
            name="RequestCollaboration",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "requested_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Pedido em"),
                ),
                (
                    "canceled_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Cancelado em"
                    ),
                ),
                (
                    "received_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Recebido em"
                    ),
                ),
                (
                    "type_collaboration",
                    models.CharField(blank=True, max_length=60, null=True),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RequestCollaborationGeneralOrgan",
            fields=[
                (
                    "requestcollaboration_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.RequestCollaboration",
                    ),
                ),
                (
                    "general_organ",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="collaborations",
                        to="rh.OrgaoGeral",
                    ),
                ),
            ],
            bases=("judicial.requestcollaboration",),
        ),
        migrations.CreateModel(
            name="RequestCollaborationPerson",
            fields=[
                (
                    "requestcollaboration_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="judicial.RequestCollaboration",
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="collaborations",
                        to="rh.Pessoa",
                    ),
                ),
            ],
            bases=("judicial.requestcollaboration",),
        ),
        migrations.AddField(
            model_name="requestcollaboration",
            name="canceled_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Cancelado por",
            ),
        ),
        migrations.AddField(
            model_name="requestcollaboration",
            name="lawsuit",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="requestcollaboration",
                to="judicial.OutCourtLawsuit",
            ),
        ),
        migrations.AddField(
            model_name="requestcollaboration",
            name="origin_location",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="requestcollaboration",
                to="rh.OrgaoGeral",
                verbose_name="Departamento de origem",
            ),
        ),
        migrations.AddField(
            model_name="requestcollaboration",
            name="received_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Recebido por",
            ),
        ),
        migrations.AddField(
            model_name="requestcollaboration",
            name="requested_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="requestcollaboration",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Pedido por",
            ),
        ),
        migrations.AddField(
            model_name="legalclassification",
            name="collaborator_can_sign",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="workerreminder",
            name="resolved_at",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Conclu\xc3\xaddo em"
            ),
        ),
        migrations.AddField(
            model_name="workerreminder",
            name="resolved_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Conclu\xc3\xaddo por",
            ),
        ),
        migrations.AddField(
            model_name="requestcollaboration",
            name="protocol_movement",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="protocolo.Movimentacao",
                verbose_name="Certid\xe3o de recebimento",
            ),
        ),
        migrations.RunPython(up_update_data, down_fake),
    ]
