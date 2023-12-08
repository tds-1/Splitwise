"""splitwise_ext URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import include, path

from splitwise_api.views import (
    CreateSingleTransaction,
    LogoutView,
    SplitwiseAuthView,
    SplitwiseCallbackView,
    UserGroupsInfoView,
    UserInfoView,
    UploadCsvView,
    GetTransactions,
    UserFriendsInfoView,
    CreateBulkTransactions,
)

urlpatterns = [
    path("splitwise/auth/", SplitwiseAuthView.as_view(), name="splitwise_auth"),
    path("splitwise/callback", SplitwiseCallbackView.as_view(), name="splitwise_callback"),
    path("splitwise/user_info/", UserInfoView.as_view(), name="splitwise_user_info"),
    path("splitwise/groups_info/", UserGroupsInfoView.as_view(), name="splitwise_user_info"),
    path('splitwise/upload_csv/', UploadCsvView.as_view(), name='upload_csv'),
    path('splitwise/get_transaction', GetTransactions.as_view(), name='get_transaction'),
    path("splitwise/groups_info/", UserGroupsInfoView.as_view(), name="splitwise_groups_info"),
    path("splitwise/friends_info/", UserFriendsInfoView.as_view(), name="splitwise_friends_info"),
    path("splitwise/logout/", LogoutView.as_view(), name="logout"),
    path("splitwise/create_bulk_transactions/", CreateBulkTransactions.as_view(), name="create_bulk_transactions"),
    path("splitwise/create_single_transaction/",  CreateSingleTransaction.as_view(), name="create_single_transaction"),
    path("splitwise/", include("splitwise_api.urls")),
]
