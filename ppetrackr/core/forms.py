from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import modelformset_factory
from timezone_field import TimeZoneFormField

from .models import Inventory, Organization, PPEType


class OnboardConnectForm(forms.Form):
    organization_code = forms.CharField(
        max_length=200,
        help_text="Enter the code if given to you by an Organization",
        required=True,
    )

    def clean_organization_code(self):
        code = self.cleaned_data["organization_code"]
        # only link the user to an org if they provide a code
        organization = Organization.objects.filter(code=code).first()
        if not organization:
            raise forms.validationerror("Sorry, this is an invalid code.")
        else:
            self.cleaned_data["organization"] = organization
        return code


class OnboardNewProviderForm(forms.ModelForm):
    # TODO: add parent_code option
    class Meta:
        model = Organization
        fields = ("name",)
        help_texts = {
            "name": "Be as specific as possible (e.g. Your Hospital Name)",
        }

class OnboardNewParentForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ("name",)
        help_texts = {
            "name": "Be as specific as possible (e.g. Your Government Body Name, Your Hospital System Name)"
        }

class AdminUserCreationForm(UserCreationForm):
    organization_name = forms.CharField(max_length=200)

    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "email",
        )


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "email", "first_name", "last_name", "timezone")


class TrackInventoryForm(forms.ModelForm):
    ppe_type = None
    ppetype = forms.ModelChoiceField(
        queryset=None, help_text="PPE Brand & Size", label="PPE Type"
    )

    field_order = [
        "ppetype",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ppetype"].queryset = PPEType.objects.filter(
            item_type=self.get_ppe_type()
        )
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.html5_required = True

    def get_ppe_type(self):
        raise NotImplementedError

    class Meta:
        model = Inventory
        exclude = (
            "item_type",
            "user",
            "timestamp",
            "organization",
        )


class TrackMaskForm(TrackInventoryForm):
    def get_ppe_type(self):
        return PPEType.N95MASK

    class Meta(TrackInventoryForm.Meta):
        help_texts = {
            "number": "Current stock of selected N95 Masks",
            "item_number": "Model number of selected N95 Masks",
            "daily_use": "Current daily use of selected N95 Masks",
            "projected_daily_use": "Projected use of selected N95 Masks tomorrow",
            "projected_run_out": "Projected date (format: YYYY-MM-DD) facility will run out of selected N95 Masks",
        }
        labels = {"item_number": "Model number"}


class TrackGloveForm(TrackInventoryForm):
    box_count = forms.IntegerField(min_value=0)

    field_order = TrackInventoryForm.field_order + ["number", "box_count"]

    def get_ppe_type(self):
        return PPEType.GLOVES

    def clean(self):
        cleaned_data = super().clean()
        number = cleaned_data["number"]
        box_count = cleaned_data["box_count"]
        cleaned_data["number"] = number * box_count
        return cleaned_data

    class Meta(TrackInventoryForm.Meta):
        help_texts = {
            "number": "Current number of selected Gloves per box",
            "box_count": "Number of boxes",
            "item_number": "Model number of selected Gloves",
            "daily_use": "Current daily use of selected Gloves",
            "projected_daily_use": "Projected use of selected Gloves tomorrow",
            "projected_run_out": "Projected date (format: YYYY-MM-DD) facility will run out of selected Gloves",
        }
        labels = {"item_number": "Model number", "number": "Glove count"}


class TrackAlcoholForm(TrackInventoryForm):
    def get_ppe_type(self):
        return PPEType.ALCOHOL

    class Meta(TrackInventoryForm.Meta):
        help_texts = {
            "number": "Current number of Rubbing Alcohol containers of solution",
            "item_number": "Model number of selected Rubbing Alcohol container",
            "daily_use": "Current daily use in fl oz of selected Rubbing Alcohol",
            "projected_daily_use": "Projected use in fl oz of selected Rubbing Alcohol tomorrow",
            "projected_run_out": "Projected date (format: YYYY-MM-DD) facility will run out of selected Rubbing Alcohol",
        }
        labels = {"item_number": "Model number"}


class TrackSwabForm(TrackInventoryForm):
    package_count = forms.IntegerField(min_value=0)

    field_order = TrackInventoryForm.field_order + ["number", "package_count"]

    def get_ppe_type(self):
        return PPEType.SWAB

    def clean(self):
        cleaned_data = super().clean()
        number = cleaned_data["number"]
        package_count = cleaned_data["package_count"]
        cleaned_data["number"] = number * package_count
        return cleaned_data

    class Meta(TrackInventoryForm.Meta):
        help_texts = {
            "number": "Number of Swabs per package",
            "package_count": "Number of packages",
            "item_number": "Model number of selected Swabs",
            "daily_use": "Current daily use of selected Swabs",
            "projected_daily_use": "Projected use of selected Swabs tomorrow",
            "projected_run_out": "Projected date (format: YYYY-MM-DD) facility will run out of selected Swabs",
        }
        labels = {"item_number": "Model number", "number": "Swab count"}


class TrackGownsForm(TrackInventoryForm):
    def get_ppe_type(self):
        return PPEType.GOWNS

    class Meta(TrackInventoryForm.Meta):
        help_texts = {
            "number": "Current stock of selected Gowns",
            "item_number": "Model number of selected Gowns",
            "daily_use": "Current daily use of selected Gowns",
            "projected_daily_use": "Projected use of selected Gowns",
            "projected_run_out": "Projected date (format: YYYY-MM-DD) facility will run out of selected Gowns",
        }
        labels = {"item_number": "Model number"}


class TrackFaceMaskForm(TrackInventoryForm):
    def get_ppe_type(self):
        return PPEType.FACE_MASK

    class Meta(TrackInventoryForm.Meta):
        help_texts = {
            "number": "Current stock of selected Non-N95 Face Mask",
            "item_number": "Model number of selected Non-N95 Face Mask",
            "daily_use": "Current daily use of selected Non-N95 Face Mask",
            "projected_daily_use": "Projected use of selected Non-N95 Face Mask tomorrow",
            "projected_run_out": "Projected date (format: YYYY-MM-DD) facility will run out of selected Non-N95 Face Mask",
        }
        labels = {"item_number": "Model number"}


TrackMaskModelFormset = modelformset_factory(Inventory, form=TrackMaskForm, extra=1,)
TrackGloveModelFormset = modelformset_factory(Inventory, form=TrackGloveForm, extra=1,)
TrackAlcoholModelFormset = modelformset_factory(
    Inventory, form=TrackAlcoholForm, extra=1,
)
TrackSwabModelFormset = modelformset_factory(Inventory, form=TrackSwabForm, extra=1,)
TrackGownsModelFormset = modelformset_factory(Inventory, form=TrackGownsForm, extra=1,)
TrackFaceMaskModelFormset = modelformset_factory(
    Inventory, form=TrackFaceMaskForm, extra=1,
)
