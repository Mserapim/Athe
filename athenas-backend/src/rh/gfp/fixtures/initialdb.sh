./manage.py exportdata "GenreEvent.objects.order_by('genre_number')" --indent=2 --with-natural-keys --import-module=rh.gfp --set-fields="{'modified_by_id': 845, 'created_by_id': 845}" -o rh/gfp/fixtures/initialdb_0001_genres.json
./manage.py exportdata "SpecieEvent.objects.order_by('specie_number')" --indent=2 --with-natural-keys --import-module=rh.gfp --set-fields="{'modified_by_id': 845, 'created_by_id': 845}" -o rh/gfp/fixtures/initialdb_0002_species.json
./manage.py exportdata "IRRF.objects.order_by('data_vigencia')" --indent=2 --with-natural-keys --import-module=rh.gfp --set-fields="{'modified_by_id': 845, 'created_by_id': 845}" -o rh/gfp/fixtures/initialdb_0003_irrf.json
./manage.py exportdata "NatureEvent.objects.order_by('code')" --indent=2 --with-natural-keys --import-module=rh.gfp -o rh/gfp/fixtures/initialdb_0004_natureevents.json
./manage.py exportdata "Evento.objects.exclude(genre_event__isnull=True).order_by('genre_event__genre_number')" --indent=2 --with-natural-keys --import-module=rh.gfp --set-fields="{'modified_by_id': 845, 'created_by_id': 845}" -o rh/gfp/fixtures/initialdb_0005_events.json

./manage.py exportdata "Evento.objects.exclude(genre_event__isnull=True).order_by('genre_event__genre_number')" --indent=2 --import-module=rh.gfp -p --set-fields="{'modified_by_id': 845, 'created_by_id': 845}" -o rh/gfp/fixtures/0002_update_events.json;
./manage.py exportdata "ConfigEvent.objects.filter()" --indent=2 --import-module=rh.gfp -p --set-fields="{'modified_by_id': 845, 'created_by_id': 845}" -o rh/gfp/fixtures/0003_update_configevents.json;


./manage.py exportdata "Choice.objects.filter(cache_path='gfp.EVENT_TAGS').order_by('app_label', 'name', 'value')" -i 2 --with-natural-keys -m standard -o "rh/gfp/fixtures/esocial_tags.json" --set-fields="{'modified_by_id': 845, 'created_by_id': 845}"
./manage.py exportdata "GenreEvent.objects.filter(genre_number='099').order_by('genre_number')" --indent=2 --import-module=rh.gfp -p --set-fields="{'modified_by_id': 845, 'created_by_id': 845}" -o rh/gfp/fixtures/esocial_genres.json;
./manage.py exportdata "Evento.objects.filter(genre_event__genre_number='099').order_by('genre_event__genre_number')" --indent=2 --with-natural-keys --import-module=rh.gfp --set-fields="{'modified_by_id': 845, 'created_by_id': 845}" -o rh/gfp/fixtures/esocial_events.json
./manage.py exportdata "ConfigEvent.objects.filter(event__genre_event__genre_number='099')" --indent=2 --import-module=rh.gfp -p --set-fields="{'modified_by_id': 845, 'created_by_id': 845}" -o rh/gfp/fixtures/esocial_configevents.json;
