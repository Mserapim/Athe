from django.db import migrations, models


def _sum_values_weight_rate_fill(fields):
    return sum(fields.values())


def _calculate_rate_fill(person, fields):
    rate = 0
    for attr, value in person.__dict__.items():
        if attr in fields and value:
            rate += fields.get(attr)

    return rate / _sum_values_weight_rate_fill(fields)


def up_fill_rate_of_natural_person(apps, editor_schema):

    fileds = {"cpf": 60, "data_nascimento": 20, "nome_mae": 10, "nome_pai": 10}

    NaturalPerson = apps.get_model("rh.PessoaFisica")

    query = NaturalPerson.objects.filter(rate_fill=None)

    total = query.count()
    pos = 0
    message = ""

    for person in query:
        rate = _calculate_rate_fill(person, fileds)
        NaturalPerson.objects.filter(pk=person.pk).update(rate_fill=rate)
        print("\b" * len(message), end="")
        pos += 1
        message = f" {pos} de {total} pessoas fisicas"
        print(message, end="")
    else:
        print("\b" * len(message), end="")
        print(" " * len(message), end="")
        print("\b" * len(message), end="")


def up_fill_rate_of_legal_person(apps, editor_schema):

    fields = {"CNPJ": 60, "razao_social": 10}

    LegalPerson = apps.get_model("rh.PessoaJuridica")

    query = LegalPerson.objects.filter(rate_fill=None)

    total = query.count()
    pos = 0
    message = ""

    for person in query:
        rate = _calculate_rate_fill(person, fields)
        LegalPerson.objects.filter(pk=person.pk).update(rate_fill=rate)
        print("\b" * len(message), end="")
        pos += 1
        message = f" {pos} de {total} pessoas juridicas"
        print(message, end="")
    else:
        print("\b" * len(message), end="")
        print(" " * len(message), end="")
        print("\b" * len(message), end="")


def empty_method(*args, **kwargs):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("rh", "0128_alter_cache_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="pessoa",
            name="rate_fill",
            field=models.DecimalField(
                blank=True, decimal_places=3, max_digits=4, null=True
            ),
        ),
        migrations.RunPython(up_fill_rate_of_natural_person, empty_method),
        migrations.RunPython(up_fill_rate_of_legal_person, empty_method),
    ]
