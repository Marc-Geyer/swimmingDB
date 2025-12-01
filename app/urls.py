"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from django.views.i18n import JavaScriptCatalog

import swimpro

urlpatterns = [
    path('', include(swimpro.urls)),
    path('admin/', admin.site.urls),
]

urlpatterns += i18n_patterns(
    path('', include("swimpro.urls")),
)

# Setup needed reccurence field

# If you already have a js_info_dict dictionary, just add
# 'recurrence' to the existing 'packages' tuple.
js_info_dict = {
    'packages': ('recurrence', ),
}
# jsi18n can be anything you like here
# TODO Figure out making it work
# urlpatterns += [
#     url(r'^jsi18n/$', JavaScriptCatalog.as_view(), js_info_dict),
# ]