from django.urls import path

from . import views

urlpatterns = [
    path("splitwise/auth/", views.SplitwiseAuthView.as_view(), name="splitwise_auth"),
    path("splitwise/callback/", views.SplitwiseCallbackView.as_view(), name="splitwise_callback"),
]
