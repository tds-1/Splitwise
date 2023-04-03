# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.


class TimeStampedModel(models.Model):

    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    modified_at = models.DateTimeField(_("Modified at"), auto_now=True)

    class Meta:
        abstract = True


class SplitwiseTransaction(TimeStampedModel):

    splitwise_user_id = models.CharField(max_length=256)
    bank_transaction_id = models.CharField(max_length=256)
    bank_transaction_time = models.DateTimeField()
    transaction_amount = models.DecimalField(max_digits=8, decimal_places=2)
    splitwise_transaction_id = models.CharField(max_length=256)
    splitwise_group_id = models.CharField(max_length=256)
