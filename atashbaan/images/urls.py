from django.urls import path

from atashbaan.images.views import (
    image_delete_view,
    image_detail_view,
    image_list_view,
    image_process_view,
    image_upload_view,
)

app_name = "images"

urlpatterns = [
    path("", image_list_view, name="image_list"),
    path("<int:pk>/", image_detail_view, name="image_detail"),
    path("delete/<int:pk>/", image_delete_view, name="image_delete"),
    path("upload/", image_upload_view, name="image_upload"),
    path("process/", image_process_view, name="image_process"),
]
