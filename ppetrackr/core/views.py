import csv
from datetime import datetime
from io import BytesIO

import xlsxwriter as xlsxwriter
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views import View

from .decorators import onboard_pending, onboard_required
from .forms import (
    CustomUserCreationForm,
    OnboardConnectForm,
    OnboardNewParentForm,
    OnboardNewProviderForm,
    TrackAlcoholModelFormset,
    TrackFaceMaskModelFormset,
    TrackGloveModelFormset,
    TrackGownsModelFormset,
    TrackMaskModelFormset,
    TrackSwabModelFormset,
)
from .models import Inventory, PPEType


def index_view(request):
    ctx = {}
    return render(request, "core/index.html", ctx)


def error_404_view(request, exception):
    ctx = {}
    return render(request, "core/404.html", ctx, status=404)


def error_500_view(request, exception):
    ctx = {}
    return render(request, "core/500.html", ctx, status=500)


def error_403_view(request, exception):
    ctx = {}
    return render(request, "core/403.html", ctx, status=403)


def error_400_view(request, exception):
    ctx = {}
    return render(request, "core/400.html", ctx, status=400)


@login_required
@onboard_required
def home_view(request):
    ctx = {}
    return render(request, "core/home.html", ctx)


@login_required
@onboard_pending
def onboard_view(request):
    ctx = {}
    return render(request, "core/onboard.html", ctx)


@login_required
@onboard_pending
def onboard_connect_view(request):
    form = OnboardConnectForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            organization = form.cleaned_data["organization"]
            request.user.organization = organization
            request.user.save()
            messages.success(request, "You have joined {}".format(organization.name))
            return redirect("home_view")
    ctx = {"form": form}
    return render(request, "core/onboard_form.html", ctx)


@login_required
@onboard_pending
def onboard_new_provider_view(request):
    form = OnboardNewProviderForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            organization = form.save(commit=False)
            organization.is_provider = True
            organization.save()
            request.user.organization = organization
            request.user.save()
            msg_plain = render_to_string(
                "registration/provider_organization_code.txt", {"user": request.user}
            )
            send_mail(
                "[PPETrackr] Your organization key code!",
                msg_plain,
                settings.EMAIL_HOST_USER,
                [request.user.email,],
            )
            messages.success(
                request,
                "You have created a new provider organization: {}. Please check your email for the organization's unique code.".format(
                    organization.name
                ),
            )
            return redirect("home_view")
    ctx = {"form": form}
    return render(request, "core/onboard_form.html", ctx)


@login_required
@onboard_pending
def onboard_new_parent_view(request):
    form = OnboardNewParentForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            organization = form.save(commit=False)
            organization.is_provider = False
            organization.save()
            request.user.organization = organization
            request.user.save()
            msg_plain = render_to_string(
                "registration/admin_organization_code.txt", {"user": request.user}
            )
            send_mail(
                "[PPETrackr] Your organization key code!",
                msg_plain,
                settings.EMAIL_HOST_USER,
                [request.user.email,],
            )
            messages.success(
                request,
                "You have created a new parent organization: {}. Please check your email for the organization's unique code.".format(
                    organization.name
                ),
            )
            return redirect("home_view")
    ctx = {"form": form}
    return render(request, "core/onboard_form.html", ctx)


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("onboard_view")
    else:
        form = CustomUserCreationForm()
    return render(
        request, "registration/register.html", {"form": form, "role_name": "Provider"}
    )


class TrackInventoryView(LoginRequiredMixin, View):
    template_name = "core/track_inventory.html"
    ppe_type = None
    PPE_FORMSET_DICT = {
        PPEType.N95MASK: TrackMaskModelFormset,
        PPEType.GLOVES: TrackGloveModelFormset,
        PPEType.ALCOHOL: TrackAlcoholModelFormset,
        PPEType.SWAB: TrackSwabModelFormset,
        PPEType.GOWNS: TrackGownsModelFormset,
        PPEType.FACE_MASK: TrackFaceMaskModelFormset,
    }

    def get_ppe_name(self):
        for choice in PPEType.PPE_CHOICES:
            if choice[0] == self.ppe_type:
                return choice[1]
        return ""

    def get_formset(self, *args, **kwargs):
        return self.PPE_FORMSET_DICT[self.ppe_type](*args, **kwargs)

    def _get_recent_items(self, user, ppe_item_type):
        recent_items = Inventory.objects.filter(
            organization=user.organization, ppetype__item_type=ppe_item_type
        ).order_by("-timestamp")[:5]
        return recent_items

    def get(self, request, *args, **kwargs):
        ctx = {
            "formset": self.get_formset(queryset=Inventory.objects.none()),
            "recent_items": self._get_recent_items(request.user, self.ppe_type),
            "ppe_name": self.get_ppe_name(),
        }
        return render(request, self.template_name, ctx)

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(request.POST)
        if formset.is_valid():
            for form in formset:
                instance = form.save(commit=False)
                instance.user = request.user
                instance.organization = request.user.organization
                instance.save()
            messages.success(
                request,
                "You have submitted an update for {} different type(s) of {}".format(
                    len(formset), self.ppe_type,
                ),
            )
            return redirect("home_view")
        ctx = {
            "formset": formset,
            "recent_items": self._get_recent_items(request.user, self.ppe_type),
        }
        return render(request, self.template_name, ctx)


@login_required
@onboard_required
def dashboard_view(request):
    ctx = {}
    return render(request, "core/dashboard.html", ctx)


@login_required
@onboard_required
def inventory_list_view(request):
    inventory_qs = Inventory.objects.filter(
        organization=request.user.organization
    ).order_by("-timestamp")
    page_num = request.GET.get("page", 1)

    paginator = Paginator(inventory_qs, 15)
    try:
        inventory_list = paginator.page(page_num)
    except PageNotAnInteger:
        inventory_list = paginator.page(1)
    except EmptyPage:
        inventory_list = paginator.page(paginator.num_pages)

    ctx = {
        "inventory_list": inventory_list,
    }
    return render(request, "core/inventory_list.html", ctx)


class PseudoBuffer:
    """This is basically a mockup of the write file format that Python expects. You can use this to work with Django
    StreamingHttpResponses"""

    def write(self, v):
        return v


@login_required
@onboard_required
def download_dashboard_view(request):
    """This view provides a file, via the ?format=<filetype> interface. Options are 'csv' and 'xlsx'. When
    possible, it uses streaming HTTP responses in order to prevent timeouts from dropping large file transfers."""

    file_format = request.GET["format"]

    # I'm sure there's a better way of doing this but this is how I did it this time. The first value in each pair is
    # the pretty title text for the header of the spreadsheet. The second value is a lambda function which helps you to
    # navigate to the attributes and sub-attributes where the field value is stored under each DB entry.
    headers = [
        ["Organization", lambda x: x.organization.name],
        ["Item Category", lambda x: dict(x.ppetype.PPE_CHOICES)[x.ppetype.item_type]],
        ["Model Number", lambda x: x.item_number],
        ["Attribute", lambda x: x.ppetype.item_attribute],
        ["Size", lambda x: x.ppetype.size],
        ["Quantity", lambda x: x.number],
        ["Daily Use", lambda x: x.daily_use],
        ["Projected Daily Use", lambda x: x.projected_daily_use],
        ["Projected Run-Out Date", lambda x: x.projected_run_out],
        ["Date Submitted (UTC)", lambda x: x.timestamp],
        ["Comments", lambda x: x.comments],
    ]

    if not request.user.organization:
        raise Http404(
            "User must become part of an organization to download inventory data."
        )
    elif (
        request.user.organization.is_provider
    ):  # If the user is a solo provider, give them just their inventory.
        db_data = list(Inventory.objects.filter(organization=request.user.organization))
    else:  # If the user is an admin, give them the inventory of all of their child providers.
        providers = request.user.organization.get_descendants().filter(is_provider=True)
        db_data = list(Inventory.objects.filter(organization__in=providers))

    data = [[v[0] for v in headers]]  # Put pretty titles into data

    for (
        entry
    ) in (
        db_data
    ):  # Use lambda functions to turn each Inventory object into a cell value
        new_row = [func(entry) for k, func in headers]
        data.append(new_row)

    if file_format == "csv":  # Create a CSV
        writer = csv.writer(PseudoBuffer())
        output = (writer.writerow(row) for row in data)
        content_type = "text/csv"
    elif file_format == "xlsx":  # Create an XLSX
        output = BytesIO()
        book = xlsxwriter.Workbook(output)
        runout_date_format = book.add_format({"num_format": "yyyy-mm-dd"})
        timestamp_format = book.add_format({"num_format": "yyyy-mm-dd hh:mm:ss.000"})
        book.remove_timezone = True
        sheet = book.add_worksheet()
        for r_num, cols in enumerate(data):
            for c_num, cell in enumerate(cols):
                form = None
                if c_num == 8:
                    form = runout_date_format
                elif c_num == 9:
                    form = timestamp_format
                if not form:
                    sheet.write(r_num, c_num, cell)
                else:
                    sheet.write(r_num, c_num, cell, form)
        book.close()
        output.seek(0)
        content_type = (
            "application/vnd.openxmlformats-officedocument-spreadsheetml.sheet"
        )

    # Generate the filename.
    dt = request.user.timezone.fromutc(datetime.utcnow())
    y, m, d = dt.year, dt.month, dt.day
    filename = f"ppetrackr_data__{y}-{m:02d}-{d:02d}.{file_format}"

    # Prepare the response and send it.
    response = StreamingHttpResponse(output, content_type=content_type)
    response["Content-Disposition"] = f"attachment; filename={filename}"
    return response
