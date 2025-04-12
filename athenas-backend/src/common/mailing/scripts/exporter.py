# -*- coding:utf-8 -*-
import os
import sqlite3

from django.template.defaultfilters import slugify

from common.mailing import models
from contrib.helpers import capitalize_words

# Profile
# Group <- GRUPOS
# Treatment <- tratamento
# Company <- ORGAO
# Position <- CARGOS
# State <- CIDADE.Uf
# City <- CIDADE
# Address <- Dados
# Phone <- Dados
# Contact <- Dados


ERRORS = []
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mailing.db")
PROFILE = models.Profile.objects.get(slug="cerimonial")
STATES = {
    "AC": "Acre",
    "AL": "Alagoas",
    "AM": "Amazonas",
    "AP": "Amapá",
    "BA": "Bahia",
    "CE": "Ceará",
    "DF": "Distrito Federal",
    "ES": "Espírito Santo",
    "GO": "Goiás",
    "MA": "Maranhão",
    "MG": "Minas Gerais",
    "MS": "Mato Grosso do Sul",
    "MT": "Mato Grosso",
    "PA": "Pará",
    "PB": "Paraíba",
    "PE": "Pernambuco",
    "PI": "Piauí",
    "PR": "Paraná",
    "RJ": "Rio de Janeiro",
    "RN": "Rio Grande do Norte",
    "RO": "Rondônia",
    "RR": "Roraima",
    "RS": "Rio Grande do Sul",
    "SC": "Santa Catarinha",
    "SE": "Sergipe",
    "SP": "São Paulo",
    "TO": "Tocantins",
}


def select(conn, table):
    cursor = conn.cursor()
    return cursor.execute("SELECT * FROM %s" % table).fetchall()


def insert_group(conn):
    print("================================ Grupo ================================")
    groups = select(conn, "GRUPOS_DB")
    for row in groups:
        print("Grupo: %s" % row["Grupo"])
        slug = slugify(row["Grupo"])
        if not models.Group.objects.filter(slug=slug).exists():
            models.Group(
                name=capitalize_words(row["Grupo"].encode("u8")),
                slug=slug,
                profile=PROFILE,
            ).save()
    print("================================ Grupo ================================\n\n")


def insert_tretament(conn):
    print(
        "================================ Tratamento ================================"
    )
    treatments = select(conn, "tratamento_DB")
    for row in treatments:
        print("Tratamento: %s" % row["Tratamento"])
        slug = slugify(row["Tratamento"])
        if not models.Treatment.objects.filter(slug=slug).exists():
            models.Treatment(
                name=capitalize_words(row["Tratamento"]),
                slug=slugify(row["Tratamento"]),
            ).save()
    print(
        "================================ Tratamento ================================\n\n"
    )


def insert_company(conn):
    print("================================ Orgao ================================")
    companies = select(conn, "ORGAO_DB")
    for row in companies:
        print("Orgao: %s" % row["Orgao"])
        slug = slugify(row["Orgao"])
        if not models.Company.objects.filter(slug=slug).exists():
            models.Company(
                name=capitalize_words(row["Orgao"]), slug=slugify(row["Orgao"])
            ).save()
    print("================================ Orgao ================================\n\n")


def insert_position(conn):
    print("================================ Cargo ================================")
    positions = select(conn, "CARGOS_DB")
    for row in positions:
        print("Cargo: %s" % row["Cargo"])
        slug = slugify(row["Cargo"])
        if not models.Position.objects.filter(slug=slug).exists():
            models.Position(
                name=capitalize_words(row["Cargo"]), slug=slugify(row["Cargo"])
            ).save()
    print("================================ Cargo ================================\n\n")


def insert_city_state(conn):
    print(
        "================================ Cidade - Estado ================================"
    )
    cities = select(conn, "CIDADE_DB")
    for row in cities:
        slug = slugify(row["Cidade"])

        if not models.State.objects.filter(UF=row["Uf"]).exists():
            state = models.State(
                name=STATES[row["Uf"]], slug=slugify(STATES[row["Uf"]]), UF=row["Uf"]
            )
            state.save()
            if not models.City.objects.filter(slug=slug).exists():
                city = models.City(
                    name=capitalize_words(row["Cidade"]),
                    slug=slugify(row["Cidade"]),
                    state=state,
                )
                city.save()
            print("Cidade - Estado: %s" % city)
    print(
        "================================ Cidade - Estado ================================\n\n"
    )


def insert_address_phone_contact(conn):
    print("================================ Contato ================================")
    contacts = select(conn, "Dados_DB")
    for row in contacts:
        print("Contato: %s" % row["Nome"])
        try:
            group, created = models.Group.objects.get_or_create(
                slug=slugify(row["Grupo"]),
                defaults={"name": capitalize_words(row["Grupo"]), "profile": PROFILE},
            )

            treatment, created = models.Treatment.objects.get_or_create(
                slug=slugify(row["Tratamento"]),
                defaults={"name": capitalize_words(row["Tratamento"])},
            )

            position, created = models.Position.objects.get_or_create(
                slug=slugify(row["Cargo"]),
                defaults={"name": capitalize_words(row["Cargo"])},
            )

            company, created = models.Company.objects.get_or_create(
                slug=slugify(row["Orgao"]),
                defaults={"name": capitalize_words(row["Orgao"])},
            )

            city, created = models.City.objects.get_or_create(
                slug=slugify(row["Cidade"]),
                defaults={
                    "name": capitalize_words(row["Cidade"]),
                    "state": models.State.objects.get(UF=row["Uf"]),
                },
            )

            address = models.Address(
                locality=capitalize_words(row["Endereco"]),
                neighborhood=capitalize_words(row["Bairro"]),
                code=row["Cep"],
                city=city,
            )
            address.save()

            phone = models.Phone(
                normal=row["Telefone"], fax=row["Fax"], mobile=row["Celular"]
            )
            phone.save()

            contact = models.Contact(
                name=capitalize_words(row["Nome"]),
                slug=slugify(row["Nome"]),
                treatment=treatment,
                position=position,
                company=company,
                address=address,
                phone=phone,
                profile=PROFILE,
            )
            contact.save()
            contact.groups.add(group)
        except Exception as e:
            ERRORS.append("%s in contacat %s" % (e, row["Nome"]))
            print("Error: %s" % e)
        print("\n")
    print(
        "================================ Contato ================================\n\n"
    )


def delete_all():
    models.Contact.objects.all().delete()
    models.Group.objects.all().delete()
    models.Treatment.objects.all().delete()
    models.Company.objects.all().delete()
    models.Position.objects.all().delete()
    models.City.objects.all().delete()
    models.State.objects.all().delete()
    models.Address.objects.all().delete()
    models.Phone.objects.all().delete()


def main(flush=False):
    if flush:
        delete_all()
    print(
        "================================ Exportação ================================\n"
    )
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    insert_group(conn)
    insert_tretament(conn)
    insert_company(conn)
    insert_position(conn)
    insert_city_state(conn)
    insert_address_phone_contact(conn)
    conn.close()
    if ERRORS:
        print(
            "================================ Erros ================================\n"
        )
        for err in ERRORS:
            print(err)
        print(
            "================================ Erros ================================\n"
        )
    print(
        "================================ Exportação ================================\n"
    )


if __name__ == "__main__":
    main()
