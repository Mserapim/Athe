from standard.models import Choice


def format_category_employee(kind):
    choices = {}
    for key, value in Choice.get_choices_for(
        "rh", "CLASSIF_EMPLOYEE_BY_POSSESSION", char_field=True
    ):
        choices.update({key: value})
    return choices.get(kind, None)
