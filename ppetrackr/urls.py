"""ppetrackr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

import ppetrackr.core.dash_app

urlpatterns = [
    path("", include("ppetrackr.core.urls")),
    path("admin/", admin.site.urls),
    path("django_plotly_dash/", include("django_plotly_dash.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

admin.site.site_header = "PPE-Trackr"

handler404 = "ppetrackr.core.views.error_404_view"
handler500 = "ppetrackr.core.views.error_500_view"
handler403 = "ppetrackr.core.views.error_403_view"
handler400 = "ppetrackr.core.views.error_400_view"
