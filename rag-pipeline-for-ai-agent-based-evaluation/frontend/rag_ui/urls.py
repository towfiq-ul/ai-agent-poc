from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path("",          views.index,         name="index"),
    path("evaluate/", views.evaluate_page, name="evaluate"),

    # API proxies
    path("api/query/",        views.api_query,        name="api_query"),
    path("api/index/files/",  views.api_index_files,  name="api_index_files"),
    path("api/index/sample/", views.api_index_sample, name="api_index_sample"),
    path("api/reset/",        views.api_reset,         name="api_reset"),
    path("api/evaluate/",     views.api_evaluate,      name="api_evaluate"),
    path("api/status/",       views.api_status,        name="api_status"),
]