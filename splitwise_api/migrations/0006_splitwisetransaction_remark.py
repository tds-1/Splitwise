# Generated by Django 3.2.8 on 2023-12-09 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('splitwise_api', '0005_splitwisetransaction_meta_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='splitwisetransaction',
            name='remark',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
