# # -*- coding: utf-8 -*-
# from __future__ import unicode_literals

# from django.db import migrations, models

# from django.db.models import Max
# from raf.models import Item, Quiz, SubItem


# def down_fn(apps, schema_editor):
#     pass


# def update(apps, schema_editor):
#     Quiz.objects.filter().update(number_order=None)
#     Item.objects.filter().update(number_order=None)
#     SubItem.objects.filter().update(number_order=None)


# def match_items(apps, schema_editor):
#     for item in Item.objects.filter():
#         print(">>>>>>>>>>>>>>>>> Ligando itens aos subitens <<<<<<<<<<<<<<<<<<<<",)
#         for subitem in item.quiz.subitem_set.filter():
#             item.subitems.add(subitem)


# def ordering_quiz(apps, schema_editor):
#     for quiz in Quiz.objects.filter():
#         print(">>>>>>>>>>>>>>>>> Ordenando questionarios <<<<<<<<<<<<<<<<<<<<",)
#         number = Quiz.next_number_order(quiz)
#         Quiz.objects.filter(pk=quiz.pk).update(number_order=number)


# def ordering_item(apps, schema_editor):
#     for quiz in Quiz.objects.filter():
#         for item in quiz.item_set.all():
#             print(">>>>>>>>>>>>>>>>> Ordenando itens <<<<<<<<<<<<<<<<<<<<",)
#             number = Item.next_number_order(item)
#             Item.objects.filter(pk=item.pk).update(number_order=number)


# def ordering_subitem(apps, schema_editor):
#     for quiz in Quiz.objects.filter():
#         for sb in quiz.subitem_set.filter():
#             print(">>>>>>>>>>>>>>>>> Ordenando subitem <<<<<<<<<<<<<<<<<<<<",)
#             number = (SubItem.objects.filter(quiz=quiz).aggregate(Max('number_order')).get('number_order__max') or 0) + 1
#             SubItem.objects.filter(pk=sb.pk).update(number_order=number)


# class Migration(migrations.Migration):

#     dependencies = [
#         ('raf', '0001_initial'),
#     ]

#     operations = [
#         migrations.RunPython(update, down_fn),
#         migrations.RunPython(match_items, down_fn),
#         migrations.RunPython(ordering_quiz, down_fn),
#         migrations.RunPython(ordering_item, down_fn),
#         migrations.RunPython(ordering_subitem, down_fn)
#     ]
