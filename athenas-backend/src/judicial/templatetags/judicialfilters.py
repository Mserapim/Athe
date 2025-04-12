# -*- coding: utf-8 -*-
# import bleach

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="safely")
def safely(value):
    pass
    # return mark_safe(
    #     bleach.clean(
    #         value if value else '',
    #         tags=bleach.ALLOWED_TAGS + 'h1,h2,h3,h4,u,s,div,span,p,i,b,em,ul,li,ol,br,img,quote,pre'.split(','),
    #         strip=True,
    #         protocols=bleach.sanitizer.ALLOWED_PROTOCOLS + ['http', 'https', 'data'],
    #         attributes={
    #             '*': ['style'],
    #             'img': ['src'],
    #         },
    #         styles=bleach.sanitizer.ALLOWED_STYLES + ['text-align', 'text-decoration']
    #     )
    # )


@register.filter(name="roman")
def roman_filter(number):
    data = [
        "",
        "I",
        "II",
        "III",
        "IV",
        "V",
        "VI",
        "VII",
        "VIII",
        "IX",
        "X",
        "XI",
        "XII",
        "XIII",
        "XIV",
        "XV",
        "XVI",
        "XVII",
        "XVIII",
        "XIX",
        "XX",
        "XXI",
        "XXII",
        "XXIII",
        "XXIV",
        "XXV",
        "XXVI",
        "XXVII",
        "XXVIII",
        "XXIX",
        "XXX",
        "XXXI",
        "XXXII",
        "XXXIII",
        "XXXIV",
        "XXXV",
        "XXXVI",
        "XXXVII",
        "XXXVIII",
        "XXXIX",
        "XL",
        "XLI",
        "XLII",
        "XLIII",
        "XLIV",
        "XLV",
        "XLVI",
        "XLVII",
        "XLVIII",
        "XLIX",
        "X",
    ]

    number = int(number or 0)
    return data[number] if len(data) > number else ""


@register.filter(name="city_name")
def city_name(value):
    prepositions = ["da", "de", "do"]
    items = []

    for word in value.lower().split():
        if not word in prepositions:
            word = word.capitalize()
        items.append(word)

    return " ".join(items)
