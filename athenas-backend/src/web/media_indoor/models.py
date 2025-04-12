import random
import re
import string
import subprocess
import uuid
import os
from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils.cache import caches

from contrib.middleware import get_current_user
from contrib.utils import getLogger
from engine.mq.models import Task
from ged.models import Arquivo as GedFile
from standard.models import AuditTimestampModel

log = getLogger(__name__)


class BaseModel(AuditTimestampModel):
    name = models.CharField(verbose_name="Nome", max_length=150)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Device(BaseModel):
    ingress_code = models.CharField(
        verbose_name="Código de ingresso", max_length=8, blank=True
    )
    last_contact = models.DateTimeField(null=True, blank=True)

    def register_contact(self):
        Device.objects.filter(pk=self.pk).update(last_contact=datetime.now())

    @property
    def last_contact_age(self):
        if self.last_contact:
            return int((datetime.now() - self.last_contact).total_seconds())

        return int(datetime.now().timestamp())

    @property
    def groups(self):
        return CampaignGroup.objects.filter(devices=self)

    def _active_campaigns(self):
        return Campaign.objects.filter(active=True)

    def _general_campaigns(self):
        return self._active_campaigns().filter(campaign_configs=None)

    def _group_campaigns(self):
        return self._active_campaigns().filter(
            campaign_configs__group__in=self.groups.values("pk")
        )

    @property
    def my_campaigns(self):
        return Campaign.objects.filter(
            models.Q(pk__in=self._general_campaigns().values("pk"))
            | models.Q(pk__in=self._group_campaigns().values("pk"))
        )

    def generate_ingress_code(self):
        return "".join(
            random.choices(string.ascii_lowercase, k=3)
            + random.choices(string.digits, k=2)
        )

    def validate_ingress_code(self):
        if not self.ingress_code:
            self.ingress_code = self.generate_ingress_code()
            while self.ingress_code in list(
                self.__class__.objects.values_list("ingress_code", flat=True)
            ):
                self.ingress_code = self.generate_ingress_code()

    def save(self, *args, **kwargs):
        self.validate_ingress_code()

        super().save(*args, **kwargs)

    def __str__(self):
        return "%s [%s]" % (self.name, self.ingress_code)


class Content(BaseModel):
    KIND_CHOICES = (("image", "Imagem"), ("video", "Vídeo"))

    kind = models.CharField(
        verbose_name="Tipo de conteúdo", max_length=10, blank=True, choices=KIND_CHOICES
    )
    embed = models.CharField(verbose_name="Código de video", max_length=600, blank=True)
    file = models.ForeignKey(
        GedFile,
        verbose_name="Arquivo",
        related_name="media_indoor_content",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    @property
    def icons(self):
        """
        Retorna os ícones para serem mostrados no grid.

        Returns:
            [list]: {iconCls: 'icon-class', 'title': 'Title'}
        """

        cache = caches["default"]
        cache_key = f"mi_content_aspect_ratio.{self.id}"
        status_icon = cache.get(cache_key)

        if not status_icon:
            aspect_ratio_valid, aspect_ratio = self.check_aspect_ratio()
            if aspect_ratio_valid:
                status_icon = {
                    "iconCls": "icon-core icon-core-success",
                    "title": f"A proporção está correta {aspect_ratio}",
                }
            else:
                status_icon = {
                    "iconCls": "icon-core icon-core-error",
                    "title": f"A proporção não está correta {aspect_ratio}",
                }

            cache.set(f"mi_content_aspect_ratio.{self.id}", status_icon)

        return status_icon

    def delete_aspect_ratio_icon(self):
        cache = caches["default"]
        cache.delete(f"mi_content_aspect_ratio.{self.id}")

    def get_video_url(self):
        url = ""
        embed = self.embed.replace("\\", "")
        match = re.search('<.+ src="([a-zA-Z0-9_:\-\./\?=]+)".*>.*</.+>', embed)

        if match and len(match.groups()) > 0:

            url = match.groups()[0]
            if "?" not in url:
                url = "%s?" % url

            if "&" in url:
                url = "%s&" % url

            url = "%sautoplay=1" % url
        return url

    def check_kind(self):

        if (
            self.file
            and isinstance(self.file.mimetype, str)
            and "/" in self.file.mimetype
        ):
            return self.file.mimetype.split("/")[0]

        if self.embed:
            return "video"

    def check_aspect_ratio(self):
        aspect_ratio_valid = False

        command = f"ffprobe -v error -select_streams v:0 -show_entries stream=display_aspect_ratio -of default=nw=1:nk=1 {self.file.absolute_path}"
        result = subprocess.run(command.split(), stdout=subprocess.PIPE, shell=False)
        aspect_ratio = result.stdout.decode().splitlines()

        if aspect_ratio == ["16:9"]:
            aspect_ratio_valid = True

        return aspect_ratio_valid, aspect_ratio

    def save(self, *args, **kwargs):
        self.kind = self.check_kind()
        if not self.kind:
            raise Exception("Não foi possível identificar o tipo de conteúdo")

        super(Content, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.delete_aspect_ratio_icon()
        return super().delete(*args, **kwargs)

    def __str__(self):
        return self.file.filename


class Campaign(BaseModel):
    contents = (
        models.ManyToManyField(
            Content,
            verbose_name="Conteúdos",
            through="ContentList",
            # through_fields=('content', 'campaign')
        ),
    )

    active = models.BooleanField(default=False, verbose_name="Ativa")
    identifier = models.UUIDField(default=uuid.uuid4, editable=False)

    def transcode_content(self):
        """Esta fução realiza a junção (transcode) de todos os conteúdos da campanha para uma única saída de vídeo

        Raises:
            Exception: raise exception quando não encontra conteúdos para a campanha
        """
        from web.media_indoor.tasks import transcode_content_task

        user = get_current_user()
        if self.campaign_lists.count() > 0:
            task = Task.start(
                transcode_content_task, campaign_id=self.id, user_id=user.pk
            )

            return task
        else:
            raise Exception("Não foram encontrados conteúdos para essa campanha")

    def toggle_active(self):
        self.active = not self.active

        if self.active:
            if self.campaign_lists.count() == 0:
                raise Exception("Só é possível ativar uma campanha com conteúdos.")

            self.transcode_content()
            activated = True

        else:
            self.save(update_fields=["active"])
            activated = False
            campaign_video = os.path.join(
                settings.CACHE_PATH, "media_indoor", f"{str(self.identifier)}.mp4"
            )
            os.remove(campaign_video)

        return activated

    @property
    def video_permalink(self):
        return f"/media-indoor/{self.identifier}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class ContentList(AuditTimestampModel):
    position = models.IntegerField(verbose_name="Posição", default=0, blank=True)
    content = models.ForeignKey(
        Content,
        verbose_name="Conteúdo",
        related_name="content_lists",
        on_delete=models.CASCADE,
    )
    campaign = models.ForeignKey(
        Campaign,
        verbose_name="Campanha",
        related_name="campaign_lists",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ["position", "-content__created_at"]

    def __str__(self):
        return self.content.name

    def get_position(self):
        positions = list(
            self.campaign.campaign_lists.all().values_list("position", flat=True)
        )

        return max(positions) + 1 if positions else 1

    def move_position(self, direction):
        new_position = (
            self.position + 1
            if direction == "up" and self.position > 0
            else self.position - 1
        )

        try:
            content = self.__class__.objects.get(
                campaign=self.campaign, position=new_position
            )
        except ContentList.DoesNotExist as e:
            log.exception(e)
            raise Exception("Não foi possível modificar a posição")
        else:
            content.position = self.position
            content.save()
            self.position = (
                self.position + 1 if direction == "up" else self.position - 1
            )
            self.save()

        return True

    @classmethod
    def reorder_content(cls, campaign):
        position = 1
        for content in cls.objects.filter(campaign=campaign).order_by("position"):
            if content.position != position:
                content.position = position
                content.save()
            position += 1

    def save(self, *args, **kwargs):
        if not self.pk:
            self.position = self.get_position()

        super().save(*args, **kwargs)


class CampaignGroup(BaseModel):
    devices = models.ManyToManyField(
        Device, verbose_name="Dispositivos", related_name="in_campaign_group"
    )
    active = models.BooleanField(default=False, verbose_name="Ativo")


class ConfigCampaignGroup(AuditTimestampModel):
    group = models.ForeignKey(
        CampaignGroup,
        verbose_name="Grupo",
        related_name="group_configs",
        on_delete=models.CASCADE,
    )
    campaign = models.ForeignKey(
        Campaign,
        verbose_name="Campanha",
        related_name="campaign_configs",
        on_delete=models.CASCADE,
    )

    class Meta:
        ordering = ("group__name",)
