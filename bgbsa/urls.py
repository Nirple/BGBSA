"""
URL configuration for bgbsa project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include

from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/profile', views.account_profile_view, name='account_profile'),
    path('accounts/selling', views.account_selling_view, name='account_selling'),
    path('accounts/selling/search', views.account_selling_search_view, name='account_selling_search'),
    path('accounts/selling/create/<int:i>', views.account_selling_create_view, name='account_selling_create'),
    path('accounts/selling/edit/<slug:slug>', views.account_selling_edit_view, name='account_selling_edit'),
    path('accounts/selling/expand/<slug:slug>', views.account_selling_expand_view, name='account_selling_expand'),
    path('accounts/selling/expand/<slug:slug>/<int:pk>', views.account_selling_expand_remove_view, name='account_selling_expand_remove'),

    path('for_sale', views.for_sale_view, name='for_sale'),
    path('for_sale/<slug:slug>', views.for_sale_detail_view, name='for_sale_detail'),
    path('', views.home_view, name='home'),
]
