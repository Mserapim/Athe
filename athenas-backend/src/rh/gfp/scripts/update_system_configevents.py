# -*- coding: utf-8 -*-

#RODAR OS MIGRATES
./manage.py migrate standard 0008_auto_20180426_1520;
./manage.py migrate rh 0067_auto_20180917_1501;
./manage.py migrate rh 0068_datamigration_config;
./manage.py migrate esocial 0003_auto_20180918_1300;
./manage.py migrate gfp 0053_auto_20180917_1501;
./manage.py migrate gfp 0054_auto_20180917_1501;
./manage.py migrate gfp 0055_datamigration_event;
./manage.py migrate gfp 0056_auto_20180920_1341;

#APAGAR CONFIGEVENT GERADO E CARREGAR FIXTURE DOS CONFIGEVENT ORGANIZADOS PARA MPTO
#Entrar no controle e depois no shell do worker
from rh.gfp.models import ConfigEvent
ConfigEvent.objects.all().delete()

#Dentro do console
./manage.py loaddata rh/gfp/fixtures/config_events.json

#Carregar fixtures
./manage.py loaddata rh/fixtures/choices.json;
./manage.py loaddata esocial/fixtures/choices.json;
./manage.py loaddata esocial/fixtures/initialdb_0001_choices.json;
./manage.py loaddata esocial/fixtures/initialdb_0002_application.json;
./manage.py loaddata esocial/fixtures/initialdb_0003_controllers.json;