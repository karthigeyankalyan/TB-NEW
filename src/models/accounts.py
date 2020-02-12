import uuid
from datetime import datetime

from src.common.database import Database


class Account(object):

    def __init__(self, invoice_date, nature_of_transaction, user_id, user_name, loan_id=None, account_head=None,
                 bank_account=None, doc_account_head=None, _id=None, cheque_number=None, payment_voucher=None,
                 depositing_bank=None, adjustment_voucher=None, ledger=None, interest=None, penal_interest=None,
                 service_charge=None, principal=None, external_bank_account=None, voucher_date=None, cleared=None,
                 cheque_date=None, narration=None, clearing_debit_balance=None, clearing_credit_balance=None,
                 amount=None):
        self.invoice_date = datetime.combine(datetime.strptime(invoice_date, '%Y-%m-%d').date(),
                                             datetime.now().time())
        if voucher_date:
            self.voucher_date = datetime.combine(datetime.strptime(voucher_date, '%Y-%m-%d').date(),
                                                 datetime.now().time())
        else:
            self.voucher_date = None

        if cheque_date:
            self.cheque_date = datetime.combine(datetime.strptime(cheque_date, '%Y-%m-%d').date(),
                                                datetime.now().time())
        else:
            self.cheque_date = None

        self.nature_of_transaction = nature_of_transaction
        self.clearing_debit_balance = 0 if clearing_debit_balance is None else int(clearing_debit_balance)
        self.clearing_credit_balance = 0 if clearing_credit_balance is None else int(clearing_credit_balance)
        self.account_head = account_head
        self.doc_account_head = doc_account_head
        self.bank_account = bank_account
        self.adjustment_voucher = adjustment_voucher
        self.depositing_bank = depositing_bank
        self.amount = amount
        self.cleared = cleared
        self.ledger = ledger
        self.interest = interest
        self.penal_interest = penal_interest
        self.service_charge = service_charge
        self.principal = principal
        self.external_bank_account = external_bank_account
        self.payment_voucher = payment_voucher
        self.cheque_number = cheque_number
        self.user_id = user_id
        self.loan_id = loan_id
        self.user_name = user_name
        self.narration = narration
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='accounts', data=self.json())

    @classmethod
    def update_receipt(cls, _id, invoice_date, nature_of_transaction, account_head, bank_account, amount, user_id,
                       user_name, doc_account_head, cheque_number, payment_voucher, depositing_bank,
                       clearing_debit_balance, clearing_credit_balance, adjustment_voucher, voucher_date, ledger,
                       cleared, cheque_date, narration):
        Database.update_receipt(collection='accounts', query={'_id': _id}, invoice_date=invoice_date,
                                nature_of_transaction=nature_of_transaction, doc_account_head=doc_account_head,
                                account_head=account_head, bank_account=bank_account, amount=amount, user_id=user_id,
                                user_name=user_name, cheque_number=cheque_number, payment_voucher=payment_voucher,
                                depositing_bank=depositing_bank, adjustment_voucher=adjustment_voucher,
                                voucher_date=voucher_date, ledger=ledger, cleared=cleared, cheque_date=cheque_date,
                                narration=narration, clearing_credit_balance=clearing_credit_balance,
                                clearing_debit_balance=clearing_debit_balance)

    @classmethod
    def update_ledger_balance(cls, head_of_accounts, debit_balance, credit_balance):
        Database.update_ledger_balance(collection='accounthead', query={'Head of Accounts': head_of_accounts},
                                       credit=credit_balance, debit=debit_balance)

    def json(self):
        return {
            'invoice_date': self.invoice_date,
            'cheque_date': self.cheque_date,
            'nature_of_transaction': self.nature_of_transaction,
            'account_head': self.account_head,
            'doc_account_head': self.doc_account_head,
            'cleared': self.cleared,
            'bank_account': self.bank_account,
            'depositing_bank': self.depositing_bank,
            'adjustment_voucher': self.adjustment_voucher,
            'clearing_debit_balance': self.clearing_debit_balance,
            'clearing_credit_balance': self.clearing_credit_balance,
            'payment_voucher': self.payment_voucher,
            'voucher_date': self.voucher_date,
            'ledger': self.ledger,
            'interest': self.interest,
            'penal_interest': self.penal_interest,
            'service_charge': self.service_charge,
            'principal': self.principal,
            'external_bank_account': self.external_bank_account,
            'amount': self.amount,
            'narration': self.narration,
            'cheque_number': self.cheque_number,
            'loan_id': self.loan_id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            '_id': self._id,
        }

    @classmethod
    def from_mongo(cls, _id):
        Intent = Database.find_one(collection='accounts', query={'_id': _id})
        return cls(**Intent)

    @classmethod
    def find_by_district(cls, district):
        intent = Database.find(collection='accounts', query={'district': district})
        return [cls(**inten) for inten in intent]
