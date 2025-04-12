from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0090_change_pouch_destination_to_workplace"),
    ]

    operations = [
        migrations.AddField(
            model_name="triagepart",
            name="lawsuit",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="triageparts",
                to="judicial.OutCourtLawsuit",
            ),
        ),
        migrations.AlterField(
            model_name="pouchlawsuit",
            name="lawsuit",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="as_pouches_items",
                to="judicial.OutCourtLawsuit",
            ),
        ),
        migrations.AlterField(
            model_name="pouchlawsuit",
            name="movement_part",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="as_item_of_pouches",
                to="judicial.PartLawsuit",
            ),
        ),
        migrations.AlterField(
            model_name="pouchlawsuit",
            name="pouch",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="items",
                to="judicial.Pouch",
            ),
        ),
        migrations.AddField(
            model_name="movementlog",
            name="main_tag",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="+",
                to="judicial.Tag",
            ),
        ),
    ]
