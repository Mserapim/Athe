# -*- coding: utf-8 -*-
from django.db import transaction
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from contrib.utils import getLogger
from rh.gfp.models import ConfigEvent, Evento, GenreEvent

log = getLogger(__name__)


@receiver(m2m_changed, sender=Evento.tags.through)
def update_config_from_m2m_tags(sender, instance, action, **kargs):
    update_config_event(sender, instance, action=action, **kargs)


@receiver(m2m_changed, sender=ConfigEvent.focuses_on.through)
def update_config_from_m2m_focuses_on(sender, instance, action, **kargs):
    update_config_event(sender, instance, action=action, **kargs)


@receiver(post_save, sender=Evento)
def update_from_event(sender, instance, **kargs):
    update_config_event(sender, instance, **kargs)


def update(configs=[]):
    """Este método atualiza a lista de ConfigEvent enviada em configs.

    Args:
        configs (list): lista de ConfigEvent
    """
    for config in ConfigEvent.objects.filter(pk__in=configs).order_by("event__numero"):
        config.save()
        log.info(f"=> Updating ConfigEvent: {config}")


def update_config_event(sender, instance, action=None, **kargs):
    def get_configs(events=[]):
        """Este método retorna o ConfigEvent de cada Evento em events.

        Args:
            configs (list): lista de ConfigEvent
        """
        configs = []
        for event in Evento.objects.filter(pk__in=events):
            for config in event.configs.all():
                configs.append(config.pk)

            """Encontra ConfigEvent de eventos que são diferenças ou devoluções."""
            tags = event.tags.all().values_list("label", flat=True)
            events = [
                ge for ge in GenreEvent.objects.filter(events__tags__label__in=tags)
            ]
            for config in ConfigEvent.objects.filter(
                event__genre_event__in=events, event__tipo="P"
            ).exclude(event__specie_event__specie_number="00"):
                configs.append(config.pk)
        return configs

    pk_set = []
    if isinstance(instance, Evento):
        pk_set = [instance.pk]
    elif action in ("post_add", "post_remove"):
        pk_set = kargs.get("pk_set")

    if isinstance(instance, ConfigEvent) and action in ("pre_clear", "pre_remove"):
        events = [pk for pk in instance.focuses_on.all().values_list("pk", flat=True)]
        events = events + [instance.event.pk]
        configs = get_configs(events)
        transaction.on_commit(lambda: update(configs))
    else:
        update(get_configs(pk_set))
