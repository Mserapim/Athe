# -.- coding: utf-8 -.-
import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()

from engine.mq.models import Task
from contrib.middleware import set_current_user, get_current_user
from esocial.tasks.qualification import discouver_persons, qualificate_batch
from esocial.loaders.qualification import QualifLoader
from ged.models import Arquivo as GedFile


def run():
    set_current_user("gustavodettenborn")

    try:
        # PROCESSADO
        ged_file = GedFile.objects.get(pk=609243)
        print("ged_file")
        qe1 = QualifLoader(ged_file.absolute_path, original_basename=ged_file.filename)
        qe1.execute()  # res

        # REJEITADO
        ged_file = GedFile.objects.get(pk=609242)
        print("ged_file")
        qe = QualifLoader(ged_file.absolute_path, original_basename=ged_file.filename)
        qe.execute()  # res

    except Exception as e:
        print(e)


if __name__ == "__main__":
    run()
