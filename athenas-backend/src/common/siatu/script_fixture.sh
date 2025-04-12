#! /bin/bash
cd ..
cd ..
source bin/activate
cd project
# ./manage.py exportdata "Group.objects.filter(name__startswith='siatu')" --indent=2 --with-natural-keys --import-module=django.contrib.auth > common/siatu/fixtures/initialdb_0002_siatu_groups.json
# ./manage.py exportdata "Controller.objects.filter(controller__startswith='Siatu')" --indent=2 --with-natural-keys --import-module=engine > common/siatu/fixtures/initialdb_0003_funcionalidades.json
# ./manage.py exportdata "ControllerPermission.objects.filter(name__startswith='siatu')" --indent=2 --with-natural-keys --import-module=engine --set_fields='{"users":[]}'> common/siatu/fixtures/initialdb_0004_controllerspermissions.json
# ./manage.py exportdata "Message.objects.filter(mid__startswith='siatu')" --indent=2 --with-natural-keys --import-module=engine.notification > common/siatu/fixtures/initialdb_0005_siatu_messages.json
./manage.py exportdata "Modelo.objects.all()" --indent=2 --with-natural-keys --import-module=common.siatu > common/siatu/fixtures/initialdb_0001_modelos.json
./manage.py exportdata "Objeto.objects.all()" --indent=2 --with-natural-keys --import-module=common.siatu > common/siatu/fixtures/initialdb_0002_objetos.json
./manage.py exportdata "Servico.objects.order_by('servico_superior', 'nome')" --indent=2 --with-natural-keys --import-module=common.siatu --set-fields='{"lista_atendentes":[], "lista_gerentes": []}'> common/siatu/fixtures/initialdb_0003_servicos.json

# ./manage.py exportdata --import-module 'engine' 'Application.objects.filter(title="SIATU")' --indent 4 --outfile='siatu/fixtures/siatu_Application.json'
# ./manage.py exportdata --import-module 'engine' 'Application.objects.get(title="SIATU").controller_set.all()' --indent 4 --outfile='siatu/fixtures/siatu_Funcionalidades.json'
# ./manage.py exportdata --import-module 'engine' 'ControllerPermission.objects.get(name="siatu-admin")' --indent 4 --outfile='siatu/fixtures/siatu_ControllerPermission_Admin.json'
# ./manage.py exportdata --import-module 'engine' 'ControllerPermission.objects.get(name="siatu-gerente")' --indent 4 --outfile='siatu/fixtures/siatu_ControllerPermission_Gerentes.json'
# ./manage.py exportdata --import-module 'engine' 'ControllerPermission.objects.get(name="siatu-atendente")' --indent 4 --outfile='siatu/fixtures/siatu_ControllerPermission_Atendentes.json'
# ./manage.py exportdata --import-module 'engine' 'Group.objects.get(name="siatu-admin")' --indent 4 --outfile='siatu/fixtures/siatu_Group_Admin.json'
# ./manage.py exportdata --import-module 'engine' 'Group.objects.get(name="siatu-gerente")' --indent 4 --outfile='siatu/fixtures/siatu_Group_Gerentes.json'
# ./manage.py exportdata --import-module 'engine' 'Group.objects.get(name="siatu-atendente")' --indent 4 --outfile='siatu/fixtures/siatu_Group_Atendentes.json'
