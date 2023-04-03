from urllib.parse import urlencode

import requests
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from requests_oauthlib import OAuth2Session
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from splitwise_api.decorators import is_authenticated

from .serializers import GroupSerializer, UserSerializer
from .utils import SplitwiseUtils

CLIENT_ID = settings.SPLITWISE_CLIENT_ID
CLIENT_SECRET = settings.SPLITWISE_CLIENT_SECRET
REDIRECT_URI = "http://localhost:8000/splitwise/callback"
AUTHORIZATION_BASE_URL = "https://secure.splitwise.com/oauth/authorize"
TOKEN_URL = "https://secure.splitwise.com/oauth/token"


class JsonResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data, renderer_context={"indent": 4})
        kwargs["content_type"] = "application/json"
        super(JsonResponse, self).__init__(content, **kwargs)


class SplitwiseAuthView(APIView):
    def get(self, request):

        splitwise = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
        authorization_url, state = splitwise.authorization_url(AUTHORIZATION_BASE_URL)
        request.session["oauth_state"] = state
        return HttpResponseRedirect(authorization_url)


class SplitwiseCallbackView(APIView):
    def get(self, request):
        code = request.GET.get("code")
        state = request.GET.get("state")
        stored_state = request.session.get("oauth_state")

        if not state or not stored_state or state != stored_state:
            return Response({"error": "Invalid state"}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = requests.post(TOKEN_URL, data=urlencode(data), headers=headers)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            if access_token:
                return HttpResponseRedirect(
                    f"http://localhost:3000/set_auth_token?access_token={access_token}"
                )
            else:
                return Response(
                    {"error": "Failed to fetch user info"}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"error": "Failed to fetch access token"}, status=status.HTTP_400_BAD_REQUEST
            )


class UserInfoView(APIView):
    @is_authenticated()
    def get(self, request):
        splitwise_obj = request.splitwise_obj
        user_info = splitwise_obj.get_current_user()
        if user_info:
            serializer = UserSerializer(user_info)
            return Response({"result": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Failed to fetch user info"}, status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    @is_authenticated()
    def get(self, request):
        if "access_token" in request.session:
            del request.session["access_token"]
            return Response(
                {"detail": "You have been logged out successfully."}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"detail": "You were not logged in."}, status=status.HTTP_400_BAD_REQUEST
            )


class UserGroupsInfoView(APIView):
    @is_authenticated()
    def get(self, request):
        access_token = request.session.get("access_token")
        if not access_token:
            return JsonResponse({"error": "Access token not found in session"})
        splitwise_obj = SplitwiseUtils(access_token)
        group_info = splitwise_obj.get_groups()
        if group_info:
            serializer = GroupSerializer(group_info, many=True)
            return Response({"result": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Failed to fetch user group info"}, status=status.HTTP_400_BAD_REQUEST
            )
