from django import template

register = template.Library()


@register.filter
def moeda_floatformat(value):
    # Converte o valor para float e formata utilizando o padrão de '.' para casas de milhares e ',' para casa de centavos
    try:
        float_value = float(value)
        formatted_value = (
            "{:,.2f}".format(float_value)
            .replace(",", "|")
            .replace(".", ",")
            .replace("|", ".")
        )
        return formatted_value
    except:
        return value


@register.filter
def modulo(value, divisor):
    try:
        return value % divisor == 0
    except (ValueError, TypeError):
        return False
