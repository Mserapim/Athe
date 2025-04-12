from django.db import migrations, models
import standard


class Migration(migrations.Migration):

    dependencies = [("contrato", "0033_criando_hired")]

    operations = [
        migrations.CreateModel(
            name="Ride",
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
                    "minute",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        to="contrato.minute",
                        blank=True,
                        null=True,
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        to="rh.PessoaJuridica",
                        blank=True,
                        null=True,
                        verbose_name="Instituição/Órgão",
                    ),
                ),
                (
                    "asking",
                    models.CharField(
                        max_length=100, verbose_name="Documento de Solicitação"
                    ),
                ),
                (
                    "asking_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="Data do Pedido"
                    ),
                ),
                (
                    "agreement_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="Data da Anuência"
                    ),
                ),
                (
                    "authorization_date",
                    models.DateField(
                        blank=True, null=True, verbose_name="Data de Autorização"
                    ),
                ),
                (
                    "dispatch_number",
                    models.CharField(max_length=100, verbose_name="Número do Dispacho"),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(standard.models.AuditableMixins, models.Model),
        ),
    ]
