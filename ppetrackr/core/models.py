import uuid

import pytz
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils import timezone
from mptt.models import MPTTModel, TreeForeignKey, TreeManager
from timezone_field import TimeZoneField


class Organization(MPTTModel, models.Model):
    name = models.CharField(max_length=255, db_index=True, unique=True)
    code = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    is_provider = models.BooleanField()

    def __str__(self):
        return "{}".format(self.name)


class User(AbstractUser):
    email = models.EmailField(
        verbose_name="email address", max_length=255, unique=True,
    )
    organization = models.ForeignKey(
        Organization,
        related_name="users",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    timezone = TimeZoneField(display_GMT_offset=True)

    @property
    def is_onboarded(self):
        return bool(self.organization)


class PPEType(models.Model):
    N95MASK = "n95mask"
    GLOVES = "gloves"
    ALCOHOL = "alcohol"
    SWAB = "swab"
    GOWNS = "gowns"
    FACE_MASK = "face_mask"

    PPE_CHOICES = (
        (N95MASK, "N95 Masks"),
        (GLOVES, "Gloves"),
        (ALCOHOL, "Alcohol Solutions"),
        (SWAB, "Swabs"),
        (GOWNS, "Gowns"),
        (FACE_MASK, "Non-N95 Face Masks"),
    )

    item_type = models.CharField(max_length=64, choices=PPE_CHOICES)
    item_attribute = models.CharField(max_length=255)
    size = models.CharField(max_length=255)

    def __str__(self):
        return "{} - {} ({})".format(
            self.get_item_type_display(), self.item_attribute, self.size
        )

    class Meta:
        verbose_name = "PPE Type"
        verbose_name_plural = "PPE Types"


class Inventory(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="inventories",
        db_index=True,
    )
    number = models.PositiveIntegerField()
    item_number = models.CharField(max_length=255, blank=True)
    daily_use = models.PositiveIntegerField(null=True, blank=True)
    projected_daily_use = models.PositiveIntegerField(null=True, blank=True)
    projected_run_out = models.DateField(null=True, blank=True)
    comments = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    ppetype = models.ForeignKey(
        "PPEType", related_name="inventories", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="inventories",
    )

    def __repr__(self):
        return "<Inventory of {}: {}>".format(self, self.number)

    class Meta:
        verbose_name = "Inventory"
        verbose_name_plural = "Inventories"
