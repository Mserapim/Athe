from django.forms import (
    Form,
    CharField,
    IntegerField,
    BooleanField,
    DateTimeField,
    FileField,
    ChoiceField,
    ModelMultipleChoiceField,
    ModelChoiceField,
)

from web.models import Area, Module, County, Poll, Choice, ProsecutorActionStatus


class AreaForm(Form):
    id = IntegerField(required=False)
    name = CharField()
    kind_of_content = CharField()
    modules = ModelMultipleChoiceField(required=False, queryset=Module.objects.all())
    as_link = BooleanField(required=False)
    can_share = BooleanField(required=False)
    parent = IntegerField(required=False)
    title = CharField(required=False)
    auto_create = BooleanField(required=False)
    items_no_searchable = BooleanField(required=False)


class PostForm(Form):
    area = IntegerField(required=False)
    id = IntegerField(required=False)
    title = CharField()
    text = CharField(required=False)
    position = IntegerField()
    as_link = BooleanField(required=False)
    is_index = BooleanField(required=False)
    tags = CharField(required=False)
    no_searchable = BooleanField(required=False)


class PollForm(Form):
    area = IntegerField()
    id = IntegerField(required=False)
    title = CharField()
    show_partial = BooleanField(required=False)
    # target = IntegerField()


class ChoiceForm(Form):
    poll = IntegerField()
    id = IntegerField(required=False)
    choice = CharField()
    votes = IntegerField(required=False)


class VoteForm(Form):
    poll = ModelChoiceField(
        queryset=Poll.objects.filter(Poll.if_published(), active=True)
    )
    choice = ModelChoiceField(queryset=Choice.objects.filter(active=True))


class PublicationForm(Form):
    content = IntegerField()
    published = BooleanField(required=False)
    published_date = DateTimeField(required=False, input_formats=["%d/%m/%Y"])
    publication_start = DateTimeField(required=False, input_formats=["%d/%m/%Y"])
    publication_end = DateTimeField(required=False, input_formats=["%d/%m/%Y"])
    cascade = BooleanField(required=False)


class LinkForm(Form):
    parent = IntegerField(required=False)
    id = IntegerField(required=False)
    area = IntegerField()
    title = CharField()
    position = IntegerField()
    url = CharField()
    kind = IntegerField()


class MultimediaForm(Form):
    id = IntegerField(required=False)
    post = IntegerField()
    kind = CharField()
    title = CharField()
    public_access = BooleanField(required=False)
    credits = CharField(required=False)
    position = IntegerField()
    url_embed = CharField(required=False)
    upfile = FileField(required=False)


class RelateAttachmentsForm(Form):
    post = IntegerField()
    medias = CharField()
    kind = CharField()


class RelateUserForm(Form):
    area = IntegerField()
    user = IntegerField()


class GroupPermissionsForm(Form):
    area = IntegerField()
    users = CharField()
    profile = ChoiceField(
        choices=(("adm", "Administrador"), ("rev", "Revisor"), ("ali", "Alimentador"))
    )


class ProsecutorActionStatusForm(Form):
    id = IntegerField(required=False)
    name = CharField()


class ProsecutorActionForm(Form):
    id = IntegerField(required=False)
    title = CharField()
    start_date = DateTimeField(input_formats=["%d/%m/%Y"])
    decision_date = DateTimeField(required=False, input_formats=["%d/%m/%Y"])
    filing = CharField(required=False)
    text = CharField()
    area = ModelChoiceField(queryset=Area.objects.all())
    status = ModelChoiceField(queryset=ProsecutorActionStatus.objects.all())
    county = ModelChoiceField(queryset=County.objects.all())
