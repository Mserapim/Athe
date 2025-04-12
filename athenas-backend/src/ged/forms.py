# -*- coding: utf-8 -*-
from contrib.extjs import register_field, extract_charfield
from django import forms
from ged.models import Arquivo


def extractor_fileupload_field(name, field, form):
    obj = extract_charfield(name, field, form)

    obj.update(xtype="ged-fileuploadfield")
    value = getattr(form.instance, name, None)
    if value is not None:
        obj.update(value=value.pk)

    return obj


@register_field(extractor_fileupload_field)
class FileUploadField(forms.ModelChoiceField):
    def __init__(self, *args, **kargs):
        super(FileUploadField, self).__init__(
            queryset=Arquivo.objects.all(), *args, **kargs
        )


@register_field(extractor_fileupload_field)
class TypedFileUploadField(FileUploadField):

    def __init__(self, types=[], *args, **kargs):
        super(FileUploadField, self).__init__(
            queryset=Arquivo.objects.all(), *args, **kargs
        )
        self.types = list(types)


@register_field(extractor_fileupload_field)
class ImageUploadField(TypedFileUploadField):
    def __init__(self, types=[], *args, **kargs):
        super(FileUploadField, self).__init__(
            queryset=Arquivo.objects.all(), *args, **kargs
        )

        self.types = ["image/jpeg", "image/png"]
