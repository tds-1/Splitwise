# Generated by Django 3.2.8 on 2023-12-08 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('splitwise_api', '0003_alter_splitwisetransaction_splitwise_transaction_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='splitwisetransaction',
            name='bank_transaction_id',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='splitwisetransaction',
            name='bank_transaction_time',
            field=models.DateTimeField(null=True),
        ),
    ]
