import uuid
from datetime import datetime

from src.common.database import Database


class MiniDemand(object):

    def __init__(self, loan_id, loan_category, district, district_bank, sub_bank, demand_id, demand_number=None,
                 demand_date=None, cheque_date=None, cheque_number=None, principal_demand=None,
                 principal_collected=None, penal_interest=None, belated_interest=None, service_charge=None,
                 closing_balance_principal_due=None, closing_balance_principal_ndue=None,
                 closing_balance_interest_due=None, ro_number=None, interest_demand=None, interest_collected=None,
                 loan_amount=None, no_of_demands=None, m_demand_no=None, roi=None, loan_sanction_date=None,
                 user_id=None, user_name=None, ann_id=None, _id=None, demand_reference=None,
                 opening_balance_principal_due=None, opening_balance_interest_due=None, cheque_amount=None,
                 cheque_date_issued=None):
        self.loan_id = loan_id
        self.demand_id = demand_id
        self.loan_category = loan_category
        self.district = district
        self.opening_balance_interest_due = opening_balance_interest_due
        self.opening_balance_principal_due = opening_balance_principal_due
        self.district_bank = district_bank
        self.sub_bank = sub_bank
        self.demand_number = demand_number
        self.demand_date = demand_date
        self.m_demand_no = m_demand_no
        if cheque_date:
            self.cheque_date = (datetime.combine(datetime.strptime(cheque_date, '%Y-%m-%d').date(),
                                                 datetime.now().time()))
        else:
            self.cheque_date = cheque_date

        self.cheque_number = cheque_number
        self.cheque_amount = cheque_amount
        self.demand_reference = demand_reference
        self.principal_demand = principal_demand
        self.principal_collected = principal_collected
        self.interest_demand = interest_demand
        self.interest_collected = interest_collected
        self.penal_interest = 0 if penal_interest is None else penal_interest
        self.belated_interest = 0 if belated_interest is None else belated_interest
        self.service_charge = service_charge
        self.closing_balance_principal_due = closing_balance_principal_due
        self.closing_balance_principal_ndue = closing_balance_principal_ndue
        self.closing_balance_interest_due = closing_balance_interest_due
        self.loan_amount = loan_amount
        self.roi = roi
        self.ro_number = ro_number

        if cheque_date_issued:
            self.cheque_date_issued = (datetime.combine(datetime.strptime(cheque_date_issued, '%Y-%m-%d').date(),
                                                        datetime.now().time()))
        else:
            self.cheque_date_issued = cheque_date_issued

        if loan_sanction_date:
            self.loan_sanction_date = (datetime.combine(datetime.strptime(loan_sanction_date, '%Y-%m-%d').date(),
                                                        datetime.now().time()))
        else:
            self.loan_sanction_date = loan_sanction_date
        self.user_id = user_id
        self.user_name = user_name
        self.no_of_demands = no_of_demands
        self.ann_id = ann_id
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='mDemands', data=self.json())

    @classmethod
    def update_mini_demand(cls, demand_number, demand_date, cheque_number, cheque_date, principal_collected,
                           interest_collected, demand_id, penal_interest, belated_interest, service_charge, no_of_demands,
                           closing_balance_principal_due, closing_balance_principal_ndue, closing_balance_interest_due,
                           cheque_amount, demand_reference, cheque_date_issued):
        Database.update_mini_demand(collection='mDemands', query={'_id': demand_id}, demand_number=demand_number,
                                    demand_date=demand_date, cheque_number=cheque_number, cheque_date=cheque_date,
                                    principal_collected=principal_collected, interest_collected=interest_collected,
                                    penal_interest=penal_interest, belated_interest=belated_interest,
                                    service_charge=service_charge, no_of_demands=no_of_demands,
                                    closing_balance_principal_due=closing_balance_principal_due,
                                    closing_balance_principal_ndue=closing_balance_principal_ndue,
                                    closing_balance_interest_due=closing_balance_interest_due,
                                    cheque_amount=cheque_amount, demand_reference=demand_reference,
                                    cheque_date_issued=cheque_date_issued)

    @classmethod
    def deletefrom_mongo(cls, _id):
        Database.delete_from_mongo(collection='mDemands', query={'_id': _id})

    def json(self):
        return {
            "loan_id": self.loan_id,
            "demand_id": self.demand_id,
            "loan_category": self.loan_category,
            "district": self.district,
            "district_bank": self.district_bank,
            "sub_bank": self.sub_bank,
            "opening_balance_principal_due": self.opening_balance_principal_due,
            "opening_balance_interest_due": self.opening_balance_interest_due,
            "demand_number": self.demand_number,
            "m_demand_no": self.m_demand_no,
            "demand_reference": self.demand_reference,
            "demand_date": self.demand_date,
            "cheque_date": self.cheque_date,
            "cheque_date_issued": self.cheque_date_issued,
            "cheque_amount": self.cheque_amount,
            "cheque_number": self.cheque_number,
            "principal_demand": self.principal_demand,
            "principal_collected": self.principal_collected,
            "interest_demand": self.interest_demand,
            "interest_collected": self.interest_collected,
            "penal_interest": self.penal_interest,
            "belated_interest": self.belated_interest,
            "service_charge": self.service_charge,
            "loan_amount": self.loan_amount,
            "roi": self.roi,
            "ro_number": self.ro_number,
            "closing_balance_principal_due": self.closing_balance_principal_due,
            "closing_balance_principal_ndue": self.closing_balance_principal_ndue,
            "closing_balance_interest_due": self.closing_balance_interest_due,
            "loan_sanction_date": self.loan_sanction_date,
            "user_id": self.user_id,
            "user_name": self.user_name,
            "ann_id": self.ann_id,
            "no_of_demands": self.no_of_demands,
            "_id": self._id
        }
