from django import forms


class CommonForm(forms.Form):
    id = forms.IntegerField(required=False)
    name = forms.CharField()
    description = forms.CharField(required=False)


class DeactivateForm(forms.Form):
    id = forms.IntegerField()


class WorkflowForm(CommonForm):
    pass


class VertexForm(CommonForm):
    acronym = forms.CharField(max_length=40)
    beginning = forms.BooleanField(required=False)
    workflow = forms.IntegerField()
    kind = forms.CharField()
    objective = forms.IntegerField()


class EdgeForm(forms.Form):
    slug = forms.SlugField()
    source = forms.IntegerField()
    target = forms.IntegerField()
    edge_hash = forms.CharField(required=False)


class RemoveEdgeForm(forms.Form):
    edge_hash = forms.CharField()
