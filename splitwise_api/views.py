from urllib.parse import urlencode

import requests
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from requests_oauthlib import OAuth2Session
from datetime import datetime
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
import csv
from io import StringIO
from .models import SplitwiseTransaction

from .serializers import ExpenseSerializer, GroupSerializer, SplitwiseTransactionSerializer, UserSerializer
from splitwise_api.decorators import is_authenticated

from .serializers import FriendSerializer, GroupSerializer, UserSerializer

CLIENT_ID = settings.SPLITWISE_CLIENT_ID
CLIENT_SECRET = settings.SPLITWISE_CLIENT_SECRET
REDIRECT_URI = f"{settings.API_HOST}/splitwise/callback"
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
                    f"{settings.API_HOST}/set_auth_token?access_token={access_token}"
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
        splitwise_obj = request.splitwise_obj
        group_info = splitwise_obj.get_groups()
        if group_info:
            serializer = GroupSerializer(group_info, many=True)
            return Response({"result": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Failed to fetch user group info"}, status=status.HTTP_400_BAD_REQUEST
            )

class UploadCsvView(APIView):
    @is_authenticated()
    def post(self, request):
        csv_file = request.FILES['file'].read().decode('UTF-8')
        data = StringIO(csv_file)
        reader = csv.DictReader(data)

        user_id = request.user.getId()
        transactions = []
        vendor = "paytm_wallet"
        for row in reader:
            if vendor ==  "paytm_wallet":
                date = datetime.strptime(row['Date'], "%d/%m/%Y %H:%M:%S") if row["Date"] else None
                if row["Status"] == "SUCCESS":
                    debit = float(row['Debit']) if row['Debit'] else 0.0
                else:
                    continue
                bank_transaction_id = row['Wallet Txn ID']
                description = row["Activity"] + row["Comment"]
            elif vendor ==  "paytm":
                date = datetime.strptime(row['Date and Time'], "%d-%m-%Y %H:%M:%S") if row["Date and Time"] else None
                if row["Type"] == "D":
                    debit = float(row['Amount']) if row['Amount'] else 0.0
                else:
                    continue
                bank_transaction_id = row['Reference no']
                description = row["Beneficiary name"]
            elif vendor ==  "bob":
                print(row.keys())
                if row["type"].strip() == "Credit":
                    continue
                date = datetime.strptime(row['Date'], '%d/%m/%Y') if row["Date"] else None
                debit = float(row['Amount']) if row['Amount'] else 0.0
                bank_transaction_id = row['Description']
                description = row["Description"]
            else:
                date = datetime.strptime(row['Date'], '%d/%m/%y').strftime('%Y-%m-%d') if row["Date"] else None
                debit = float(row['Debit']) if row['Debit'] else 0.0
                bank_transaction_id = row['Txn']
                description = row["Description"]
            if debit == 0:
                continue

            existing_transactions = SplitwiseTransaction.objects.filter(
                bank_transaction_id=bank_transaction_id, bank_transaction_time=date, transaction_amount=debit
            )
            obj, _ = SplitwiseTransaction.objects.get_or_create(
                bank_transaction_time=date,
                bank_transaction_desc=description,
                bank_transaction_id=bank_transaction_id,
                transaction_amount=debit,
                splitwise_user_id=user_id,
            )
            data = SplitwiseTransactionSerializer(obj).data
            transactions.append(data)

            data["existing_transaction"] = existing_transactions.filter(splitwise_transaction_id__isnull=False).exists()

        return Response({"result": transactions}, status=status.HTTP_200_OK)

class GetTransactions(APIView):
    def get(self, request):
        user_id = request.GET.get("user_id")

        transactions = SplitwiseTransaction.objects.filter(splitwise_user_id=user_id)
        serializer = SplitwiseTransactionSerializer(transactions, many=True)
        return JsonResponse(serializer.data)

class UserFriendsInfoView(APIView):
    @is_authenticated()
    def get(self, request):
        splitwise_obj = request.splitwise_obj
        friends_info = splitwise_obj.get_friends()
        if friends_info:
            serializer = FriendSerializer(friends_info, many=True)
            return Response({"result": serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Failed to fetch user group info"}, status=status.HTTP_400_BAD_REQUEST
            )

class CreateSingleTransaction(APIView):
    @is_authenticated()
    def post(self, request):
        user_id = request.user.getId()
        splitwise_obj = request.splitwise_obj
        transaction = request.data
        users = transaction["users"]
        users.append(request.user.id)
        per_head_share = (float(transaction["cost"])/len(users))
        per_head_share = round(per_head_share, 2)
        cost = per_head_share * len(users)
        user_share_mapping_list = []
        for user in users:
            paid_share = 0
            if request.user.id == user:
                paid_share = cost
            user_share_mapping_list.append({
                "id": user,
                "paid_share": paid_share,
                "owed_share": per_head_share,
            })

        obj, error = splitwise_obj.create_expense(cost, transaction["title"], transaction["groupId"], user_share_mapping_list)
        if obj:
            obj, _ = SplitwiseTransaction.objects.get_or_create(
                bank_transaction_desc=transaction["title"],
                splitwise_group_id=transaction["groupId"],
                transaction_amount=cost,
                splitwise_user_id=user_id,
                splitwise_transaction_id=obj.id,
            )
            return Response({"result": {"transaction":transaction, "success": True, "description": ""}}, status=status.HTTP_200_OK)
        if error:
            return Response({"result": {"transaction":transaction,  "success": False,"errors": error.errors}}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"result": {"transaction":transaction, "success": True, "description": ""}}, status=status.HTTP_200_OK)

class CreateBulkTransactions(APIView):
    @is_authenticated()
    def post(self, request):
        splitwise_obj = request.splitwise_obj
        data = request.data
        transactions = data["transactions"]
        result = {
            "errors": [],
            "success": [],
        }
        for transaction in transactions:
            cost = transaction["transactionDetails"]["transaction_amount"]
            title = transaction["transactionDetails"]["bank_transaction_desc"]
            group_id = transaction["group"]
            user_share_mapping_list = []
            users = transaction["users"]
            users.append(request.user.id)
            per_head_share = (float(cost)/len(users))
            per_head_share = round(per_head_share, 2)
            cost = per_head_share * len(users)
            for user in users:
                paid_share = 0
                if request.user.id == user:
                    paid_share = cost
                user_share_mapping_list.append({
                    "id": user,
                    "paid_share": paid_share,
                    "owed_share": per_head_share,
                })
            obj, error = splitwise_obj.create_expense(cost, title, group_id, user_share_mapping_list)
            if obj:
                splitwise_transaction_id = obj.id
                bank_transaction_id = transaction["transactionDetails"]["bank_transaction_id"]
                obj = SplitwiseTransaction.objects.filter(bank_transaction_id=bank_transaction_id).last()
                obj.splitwise_transaction_id = splitwise_transaction_id
                obj.save()

                splitwise_transaction_id
                result["success"].append({"transaction":transaction, "success": True, "description": ""})
            if error:
                result["errors"].append({"transaction":transaction,  "success": False,"errors": error.errors})

        return Response({"result": result}, status=status.HTTP_200_OK)
