from django.conf import settings
from splitwise import Splitwise
from splitwise.expense import Expense
from splitwise.user import ExpenseUser

CONSUMER_KEY = settings.SPLITWISE_CLIENT_ID
CONSUMER_SECRET = settings.SPLITWISE_CLIENT_SECRET


class SplitwiseUtils:
    _splitwise_api = None
    secret = None

    def __init__(self, access_token):
        self._access_token = access_token

    def get_splitwise_obj(self):
        return Splitwise(CONSUMER_KEY, CONSUMER_SECRET, api_key=self._access_token)

    def get_splitwise_user_api(self):
        sObj = self.get_splitwise_obj()
        return sObj

    def get_current_user(self):
        return self.get_splitwise_obj().getCurrentUser()

    def get_groups(self):
        return self.get_splitwise_obj().getGroups()

    def get_currencies(self):
        return self.get_splitwise_obj().getCurrencies()

    def get_group_summary(self, group_id: int):
        return self.get_splitwise_obj().getGroup(str(group_id))

    def create_expense(self, cost: int, title: str, user_share_mapping_list: list = []):
        # user_share_mapping = [{
        #     "user_id": 123,
        #     "paid_share": 0,
        #     "owed_share": 0,
        # }]
        expense = Expense()
        expense.setCost(cost)
        expense.setDescription(title)
        users = []
        for user_share_mapping in user_share_mapping_list:
            user = ExpenseUser()
            user.setId(user_share_mapping["id"])
            user.setPaidShare(user_share_mapping["paid_share"])
            user.setOwedShare(user_share_mapping["owed_share"])
            users.append(user)
        expense.setUsers(users)
        return self.get_splitwise_obj().createExpense(expense)
