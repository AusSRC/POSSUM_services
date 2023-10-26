from django.contrib import admin
from django.urls import path, reverse_lazy, include
from django.conf import settings

from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

from survey import views

admin.site.site_header = "POSSUM Survey"
admin.site.site_title = "POSSUM Survey"
admin.site.index_title = "POSSUM Survey"

urlpatterns = []

if settings.LOCAL is False:
    urlpatterns.append(path('admin/login/', RedirectView.as_view(url=settings.LOGIN_URL, permanent=True, query_string=True)))
    urlpatterns.append(path("admin/logout/", views.logout_view, name="logout_view"))

urlpatterns += [
    path('', RedirectView.as_view(url=reverse_lazy('admin:index'))),
    path("admin/", admin.site.urls),
    path("oauth/", include('social_django.urls', namespace="social")),
]

