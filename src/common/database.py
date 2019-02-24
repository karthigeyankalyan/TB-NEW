import os

import pymongo


class Database(object):
    # URI = os.environ['MONGODB_URI']
    # DATABASE = None
    #
    # @staticmethod
    # def initialize():
    #     client = pymongo.MongoClient(Database.URI)
    #     Database.DATABASE = client['heroku_xwlzxcmr']

    URI = "mongodb://127.0.0.1:27017"
    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client['TABCEDCO']

    @staticmethod
    def insert(collection, data):
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection, query):
        return Database.DATABASE[collection].find(query)

    @staticmethod
    def find_one(collection, query):
        return Database.DATABASE[collection].find_one(query)

    @staticmethod
    def update_receipt(collection, query, invoice_date, nature_of_transaction, account_head, bank_account, amount,
                       user_id, user_name, doc_account_head, cheque_number, payment_voucher, depositing_bank,
                       adjustment_voucher, voucher_date, ledger, cleared, cheque_date, narration):

        return Database.DATABASE[collection].update_one(query, {'$set': {'invoice_date': invoice_date,
                                                                         'cheque_date': cheque_date,
                                                                         'nature_of_transaction': nature_of_transaction,
                                                                         'account_head': account_head,
                                                                         'doc_account_head': doc_account_head,
                                                                         'bank_account': bank_account,
                                                                         'depositing_bank': depositing_bank,
                                                                         'adjustment_voucher': adjustment_voucher,
                                                                         'payment_voucher': payment_voucher,
                                                                         'voucher_date': voucher_date,
                                                                         'ledger': ledger,
                                                                         'cleared': cleared,
                                                                         'amount': amount,
                                                                         'narration': narration,
                                                                         'cheque_number': cheque_number,
                                                                         'user_id': user_id,
                                                                         'user_name': user_name}}, True)

    @staticmethod
    def update_balance(collection, query, amount, changed_on_date):
        return Database.DATABASE[collection].update_one(query, {'$set': {'amount': amount,
                                                                         'changed_on_date': changed_on_date}}, True)

    @staticmethod
    def update_application(collection, query, applicant_name, loan_category, age, gender, address, district, roi,
                           annual_income, caste, bank, loan_reason, loan_amount, received_date, status, status_date,
                           ann_loan_id, user_id, user_name, shg_name, amount_per_member, strength, no_of_shgs,
                           cheque_number, no_of_demands, sb, amount_to_pay, father_name, loan_number, jr_letter_date,
                           jr_letter_number, screening_date, pso_date, ro_date, ro_number, post_pso_ref,
                           bank_district, cheque_date):

        amount_per_member = 0 if amount_per_member is None else amount_per_member
        strength = 0 if strength is None else strength

        return Database.DATABASE[collection].update_one(query, {'$set': {'applicant_name': applicant_name,
                                                                         'father_name': father_name,
                                                                         'loan_category': loan_category,
                                                                         'age': age,
                                                                         'gender': gender,
                                                                         'address': address,
                                                                         'district': district,
                                                                         'bank_district': bank_district,
                                                                         'caste': caste,
                                                                         'annual_income': annual_income,
                                                                         'bank': bank,
                                                                         'sub_bank': sb,
                                                                         'loan_reason': loan_reason,
                                                                         'loan_number': loan_number,
                                                                         'received_date': received_date,
                                                                         'screening_date': screening_date,
                                                                         'jr_letter_date': jr_letter_date,
                                                                         'pso_date': pso_date,
                                                                         'ro_date': ro_date,
                                                                         'jr_letter_number': jr_letter_number,
                                                                         'status': status,
                                                                         'status_date': status_date,
                                                                         'ann_loan_id': ann_loan_id,
                                                                         'loan_amount': loan_amount,
                                                                         'roi': roi,
                                                                         'no_of_demands': no_of_demands,
                                                                         'user_name': user_name,
                                                                         'user_id': user_id,
                                                                         'no_of_shgs': no_of_shgs,
                                                                         'strength': strength,
                                                                         'shg_name': shg_name,
                                                                         'ro_number': ro_number,
                                                                         'post_pso_ref_no': post_pso_ref,
                                                                         'amount_per_member': amount_per_member,
                                                                         'cheque_date': cheque_date,
                                                                         'total_amount':
                                                                             int(amount_per_member)*int(strength),
                                                                         'cheque_number': cheque_number,
                                                                         "amount_yet_to_pay":
                                                                             amount_to_pay}}, True)

    @staticmethod
    def update_demand(collection, query, demand_number, demand_date, cheque_number, cheque_date, principal_collected,
                      interest_collected, penal_interest, belated_interest, service_charge, no_of_demands,
                      closing_balance_principal_due, closing_balance_principal_ndue, closing_balance_interest_due):
        return Database.DATABASE[collection].update_one(query, {'$set': {'demand_number': demand_number,
                                                                         "demand_date": demand_date,
                                                                         "cheque_date": cheque_date,
                                                                         "cheque_number": cheque_number,
                                                                         "principal_collected": principal_collected,
                                                                         "interest_collected": interest_collected,
                                                                         "penal_interest": penal_interest,
                                                                         "belated_interest": belated_interest,
                                                                         "service_charge": service_charge,
                                                                         "no_of_demands": no_of_demands,
                                                                         "closing_balance_principal_due":
                                                                             closing_balance_principal_due,
                                                                         "closing_balance_principal_ndue":
                                                                             closing_balance_principal_ndue,
                                                                         "closing_balance_interest_due":
                                                                             closing_balance_interest_due}}, True)

    @staticmethod
    def update_pending_amount(collection, query, amount_yet_to_be_paid):
        return Database.DATABASE[collection].update_one(query, {'$set':
                                                                {"amount_yet_to_pay": amount_yet_to_be_paid}}, True)

    @staticmethod
    def delete_from_mongo(collection, query):
        print(query)
        Database.DATABASE[collection].remove(query)
