"""URL routing for the Interface layer.

Maps the single endpoint this demo exposes to its view function. Kept
separate from ``views.py`` so routing concerns never mix with request
handling.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("bookings/", views.create_booking, name="create_booking"),
]
