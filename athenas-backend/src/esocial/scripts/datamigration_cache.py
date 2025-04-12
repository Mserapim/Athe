# -.- coding: utf-8 -.-
import django
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "app.settings"

django.setup()


def run_datamigration():
    from esocial.models import Event

    print("Modificando modified_by_event_cache batch_cache.")

    query = Event.objects.filter().exclude(internal=True)
    total = query.count()
    count = 0
    print(f"Modificando Event {count} de {total}...")
    for event in query.order_by("acronym"):
        count += 1
        modified_by_event_cache = event.get_modified_by_event_cache()
        batch_cache = event.get_batch_cache()
        message = f"Modificando {count} de {total}: {event.acronym} ({event.id}) ({event.process_status}) para "
        if modified_by_event_cache:
            message += f" modified_by_event_cache({modified_by_event_cache})"
        if batch_cache:
            message += f" batch_cache({batch_cache})"

        Event.objects.filter(pk=event.pk).update(
            modified_by_event_cache=modified_by_event_cache, batch_cache=batch_cache
        )

        print(message)
    print(f"Finalizado {count} de {total}.")


if __name__ == "__main__":
    print(
        """Este scritp atualiza modified_by_event_cache batch_cache dos eventos que possuem estes valores."""
    )
    run_datamigration()
