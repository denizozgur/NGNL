# --- FILE: ngnl/urls.py ---
from django.contrib import admin
from django.urls import path, include # Make sure 'include' is imported

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')), # Include all URLs from the core app
]