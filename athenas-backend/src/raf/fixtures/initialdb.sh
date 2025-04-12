./manage.py exportdata "Application.objects.order_by('layer', 'title').filter(title__icontains='RAF')" --indent=2 --with-natural-keys --import-module=engine > raf/fixtures/00-menu.json
./manage.py exportdata "Controller.objects.filter(application__title__icontains='RAF').order_by('module', 'title')" --indent=2 --with-natural-keys --import-module=engine >> raf/fixtures/00-menu.json
./manage.py exportdata "Choice.objects.filter(app_label='raf')" --indent=2 --with-natural-keys --import-module=raf --set-fields="{'modified_by_id': 845, 'created_by_id': 845}"> raf/fixtures/01-choices.json
