# -*- coding:utf-8 -*-
from corregedoria.reportbuilder.test.report import MyReport


if __name__ == "__main__":
    print("Teste report")
    report = MyReport(output_file="meu_arquivo.pdf")
    report.build()
