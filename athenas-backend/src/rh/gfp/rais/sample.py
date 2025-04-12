# -*- coding: utf-8 -*-

from rh.gfp.rais import RegistroServidor
from rh.models import Servidor
from rh.gfp.rais import File

with open("/home/rodrigomatias/rais-2011.txt", "w") as fd:
    fd.write(str(File({"ano_base": 2011})))

# Remuneracao

RegistroServidor(2011, Servidor.objects.get(matricula=8291), 0).remuneracao(12)
quit

# BUG

RegistroServidor(2011, Servidor.objects.get(matricula=72107), 0)
RegistroServidor(2011, Servidor.objects.get(matricula=19398), 0)
RegistroServidor(2011, Servidor.objects.get(matricula=100110), 0)
RegistroServidor(2011, Servidor.objects.get(matricula=104510), 0)
quit

# Salario Contratual

for mat in (
    104210,
    107310,
    105410,
    83608,
    3290,
    105010,
    103910,
    83408,
    1001922,
    90408,
    103110,
    73307,
    66007,
    98510,
    78207,
    108910,
    97109,
    98710,
    106310,
):
    try:
        RegistroServidor(
            2011, Servidor.objects.get(matricula=mat), 0
        ).salario_contratual
    except:
        print(mat, "ERR")

quit

# CBO

RegistroServidor(2011, Servidor.objects.get(matricula=66807), 0).cbo
RegistroServidor(2011, Servidor.objects.get(matricula=97109), 0).cbo
RegistroServidor(2011, Servidor.objects.get(matricula=83608), 0).cbo
RegistroServidor(2011, Servidor.objects.get(matricula=8216614), 0).cbo
RegistroServidor(2011, Servidor.objects.get(matricula=1001922), 0).cbo
quit
