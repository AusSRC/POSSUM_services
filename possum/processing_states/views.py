from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.conf import settings
import urllib.parse


def logout_view(request):
  logout(request)
  url = settings.LOGOUT_URL + '?redirect_uri=' + urllib.parse.quote(f"https://{request.get_host()}/admin")
  return redirect(url)