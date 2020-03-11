import uuid
from datetime import datetime

from src.common.database import Database


class Ledger(object):

    def __init__(self, head_of_account, opening_balance_debit, opening_balance_credit, _id=None):
        self.head_of_account = head_of_account
        self.opening_balance_credit = opening_balance_credit
        self.opening_balance_debit = opening_balance_debit
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='accounthead', data=self.json())

    @classmethod
    def update_account_head_opening_balance(cls, _id, head_of_account, opening_balance_debit, opening_balance_credit):
        Database.update_account_head_opening_balance(collection='accounthead', query={'_id': _id},
                                                     account_head=head_of_account,
                                                     opening_balance_debit=opening_balance_debit,
                                                     opening_balance_credit=opening_balance_credit)

    def json(self):
        return {
            'Head of Accounts': self.head_of_account,
            'Cl': {
                'Debit Bal': self.opening_balance_debit,
                'Credit Bal': self.opening_balance_credit
            },
            '_id': self._id
        }

    @classmethod
    def from_mongo(cls, _id):
        Intent = Database.find_one(collection='accounts', query={'_id': _id})
        return cls(**Intent)

    @classmethod
    def find_by_district(cls, district):
        intent = Database.find(collection='accounts', query={'district': district})
        return [cls(**inten) for inten in intent]
