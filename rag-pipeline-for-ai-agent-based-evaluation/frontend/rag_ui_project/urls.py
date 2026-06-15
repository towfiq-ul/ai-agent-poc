from django.urls import path, include

urlpatterns = [
    path("", include("rag_ui.urls")),
]
