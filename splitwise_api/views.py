import requests
from requests_oauthlib import OAuth2Session
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.conf import settings
from rest_framework.views import APIView
from urllib.parse import urlencode
from .utils import SplitwiseUtils
from .serializers import GroupSerializer, UserSerializer
from rest_framework.renderers import JSONRenderer


CLIENT_ID = settings.SPLITWISE_CLIENT_ID
CLIENT_SECRET = settings.SPLITWISE_CLIENT_SECRET
REDIRECT_URI = 'http://localhost:8000/splitwise/callback/'
AUTHORIZATION_BASE_URL = 'https://secure.splitwise.com/oauth/authorize'
TOKEN_URL = 'https://secure.splitwise.com/oauth/token'

class JsonResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data, renderer_context={'indent':4})
        kwargs['content_type'] = 'application/json'
        super(JsonResponse, self).__init__(content, **kwargs)

class SplitwiseAuthView(APIView):
    def get(self, request):
        splitwise = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
        authorization_url, state = splitwise.authorization_url(AUTHORIZATION_BASE_URL)
        request.session['oauth_state'] = state
        return HttpResponseRedirect(authorization_url)

class SplitwiseCallbackView(APIView):
    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')
        stored_state = request.session.get('oauth_state')

        if not state or not stored_state or state != stored_state:
            return JsonResponse({'error': 'Invalid state'})

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        response = requests.post(TOKEN_URL, data=urlencode(data), headers=headers)
        if response.status_code == 200:
            token_data = response.json()
            request.session['access_token'] = token_data['access_token']
            return JsonResponse({'success': 'Access token and refresh token saved in session'})
        else:
            return JsonResponse({'error': 'Failed to fetch access token'})


class UserInfoView(APIView):
    def get(self, request):
        access_token = request.session.get('access_token')
        if not access_token:
            return JsonResponse({'error': 'Access token not found in session'})
        splitwise_obj = SplitwiseUtils(access_token)
        user_info = splitwise_obj.get_current_user()
        if user_info:
            serializer = UserSerializer(user_info)
            return JsonResponse({'result': serializer.data})
        else:
            return JsonResponse({'error': 'Failed to fetch user info'})

class UserGroupsInfoView(APIView):
    def get(self, request):
        access_token = request.session.get('access_token')
        if not access_token:
            return JsonResponse({'error': 'Access token not found in session'})
        splitwise_obj = SplitwiseUtils(access_token)
        group_info = splitwise_obj.get_groups()
        if group_info:
            serializer = GroupSerializer(group_info, many=True)
            return JsonResponse({'result': serializer.data})
        else:
            return JsonResponse({'error': 'Failed to fetch user info'})

