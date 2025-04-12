import csv
import os

from bs4 import BeautifulSoup
import django
from django.conf import settings

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"
BASE_LOCATION = settings.BASE_DIR

django.setup()


def html_table_to_csv(html_path, file_name):
    csvs_location = f"{BASE_LOCATION}/esocial/data/generated/csv/{file_name}.csv"
    with open(csvs_location, "w", newline="", encoding="UTF-8") as outfile:
        writer = csv.writer(outfile, delimiter="|")
        with open(html_path, encoding="UTF-8") as html_file:
            tree = BeautifulSoup(html_file, features="html.parser")
            table_tag = tree.select("table")[0]
            tab_data = []
            for row_data in table_tag.select("tr"):
                inner_list = []
                for idx, item in enumerate(row_data.select("th, td")):
                    new_item = item.text.replace("\n", "").strip(" ")
                    if idx == 6:
                        new_item = new_item[-2:]
                        new_item = (
                            new_item.strip("-")
                            if new_item.startswith("-") and len(new_item) == 2
                            else new_item
                        )
                        inner_list.append(new_item)
                    else:
                        inner_list.append(new_item)
                tab_data.append(inner_list)
        # Removendo cabeçalho da tabela
        tab_data.pop(0)
        for data in tab_data:
            writer.writerow(data)


def generate_csv_from_html():
    path = f"{BASE_LOCATION}/esocial/data/schema/htmls"
    files = os.listdir(path)
    for file in files:
        file_name = file.split(".")[0]
        html_path = f"{BASE_LOCATION}/esocial/data/schema/htmls/{file}"
        html_table_to_csv(html_path, file_name)


if __name__ == "__main__":
    generate_csv_from_html()
