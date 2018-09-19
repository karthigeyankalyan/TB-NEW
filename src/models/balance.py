import uuid
from datetime import datetime

from src.common.database import Database


class Balance(object):

    def __init__(self, changed_on_date, account_name, amount, _id=None):
        self.changed_on_date = datetime.combine(datetime.strptime(changed_on_date, '%Y-%m-%d').date(),
                                                datetime.now().time())
        self.amount = amount
        self.account_name = account_name
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='balances', data=self.json())

    @classmethod
    def update_balance_amount(cls, changed_on_date, account_name, amount):
        Database.update_balance(collection='accounts', query={'account_name': account_name}, amount=amount,
                                changed_on_date=changed_on_date)

    def json(self):
        return {
            'amount': self.amount,
            'changed_on_date': self.changed_on_date,
            'account_name': self.account_name,
            '_id': self._id,
        }
