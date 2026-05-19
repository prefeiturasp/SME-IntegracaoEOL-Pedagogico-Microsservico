"""Modelos base do microsserviço pedagógico."""

from django.db import models


class ModeloBase(models.Model):
    """Base para modelos que não são gerenciados pelo Django."""

    class Meta:
        abstract = True
        managed = False
