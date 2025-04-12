from django.db import models
from django.template.defaultfilters import slugify
from edocs.protocolo.models import TipoDocumento as DocumentType
from rh.models import Lotacao as Workplace
from standard.models import AuditTimestampModel


class Channel(AuditTimestampModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, db_index=True, blank=True)
    workplace = models.ForeignKey(
        Workplace, related_name="channels", on_delete=models.CASCADE
    )
    document_type = models.ForeignKey(
        DocumentType, related_name="channels", on_delete=models.CASCADE
    )

    def make_slug(self):
        if not self.slug:
            slug = slugify(self.name)

            qs = Channel.objects.filter(slug__startswith=slug)
            if qs.exists():
                slug = "%s-%s" % (slug, qs.count())

            self.slug = slug

    def save(self, *args, **kwargs):
        self.make_slug()
        super(Channel, self).save(*args, **kwargs)
