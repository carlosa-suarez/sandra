from django.urls import path

from . import views

urlpatterns = [
    path("complains", views.index),
    path("upload/", views.upload_pdf_view, name="upload_pdf"),
]