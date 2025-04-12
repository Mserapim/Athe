from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("judicial", "0093_add_field_in_officerdiligence"),
    ]

    operations = [
        migrations.AddField(
            model_name="additionaldiligence",
            name="dispatch_title",
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="recomendation",
            name="dispatch_title",
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
