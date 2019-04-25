import uuid
from datetime import datetime

from src.common.database import Database


class LoanApplication(object):
    def __init__(self, loan_category, district, caste, bank, roi, loan_reason, received_date, status, status_date,
                 no_of_demands, ann_loan_id, loan_amount, user_id, user_name, annual_income=None, age=None, gender=None,
                 address=None, applicant_name=None, shg_name=None, strength=None, amount_per_member=None,
                 cheque_number=None, sub_bank=None, final_collection_amount=None, _id=None, ro_number=None,
                 amount_yet_to_pay=None, no_of_shgs=None, father_name=None, screening_date=None, loan_number=None,
                 jr_letter_date=None, jr_letter_number=None, pso_date=None, ro_date=None, post_pso_ref_no=None,
                 bank_district=None, cheque_date=None):
        self.applicant_name = applicant_name
        self.father_name = father_name
        self.loan_category = loan_category
        self.age = age
        self.gender = gender
        self.address = address
        self.district = district
        self.caste = caste
        self.annual_income = annual_income
        self.bank = bank
        self.sub_bank = sub_bank
        self.loan_reason = loan_reason
        self.jr_letter_number = jr_letter_number
        self.ro_number = ro_number
        self.post_pso_ref_no = post_pso_ref_no
        self.bank_district = bank_district

        if jr_letter_date:
            self.jr_letter_date = (datetime.combine(datetime.strptime(jr_letter_date, '%Y-%m-%d').date(),
                                                    datetime.now().time()))
        else:
            self.jr_letter_date = jr_letter_date

        if cheque_date:
            self.cheque_date = (datetime.combine(datetime.strptime(cheque_date, '%Y-%m-%d').date(),
                                                 datetime.now().time()))
        else:
            self.cheque_date = cheque_date

        if pso_date:
            self.pso_date = (datetime.combine(datetime.strptime(pso_date, '%Y-%m-%d').date(),
                                              datetime.now().time()))
        else:
            self.pso_date = pso_date

        if ro_date:
            self.ro_date = (datetime.combine(datetime.strptime(ro_date, '%Y-%m-%d').date(),
                                             datetime.now().time()))
        else:
            self.ro_date = ro_date

        if received_date:
            self.received_date = (datetime.combine(datetime.strptime(received_date, '%Y-%m-%d').date(),
                                                   datetime.now().time()))
        else:
            self.received_date = received_date

        if screening_date:
            self.screening_date = (datetime.combine(datetime.strptime(screening_date, '%Y-%m-%d').date(),
                                                    datetime.now().time()))
        else:
            self.screening_date = screening_date

        self.status = status

        if status_date:
            self.status_date = (datetime.combine(datetime.strptime(status_date, '%Y-%m-%d').date(),
                                                 datetime.now().time()))
        else:
            self.status_date = status_date

        self.ann_loan_id = ann_loan_id
        self.loan_amount = loan_amount
        self.roi = roi
        self.no_of_demands = no_of_demands
        self.user_id = user_id
        self.user_name = user_name
        self.no_of_shgs = no_of_shgs
        self.shg_name = shg_name
        self.amount_per_member = amount_per_member if amount_per_member is None else int(amount_per_member)
        self.strength = strength if strength is None else int(strength)
        self.total_amount = None if strength is None else int(amount_per_member)*int(strength)
        self.cheque_number = cheque_number
        self.final_collection_amount = final_collection_amount
        self.amount_yet_to_pay = int(loan_amount)
        self.loan_number = loan_number
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_to_mongo(self):
        Database.insert(collection='loans', data=self.json())

    @classmethod
    def update_loan_app(cls, applicant_name, loan_category, age, gender, address, district, annual_income, sub_bank,
                        caste, bank, loan_reason, loan_amount, received_date, status, status_date, roi, no_of_demands,
                        ann_loan_id, user_id, user_name, loan_id, no_of_shgs, amount_per_member, strength, shg_name,
                        cheque_number, amount_to_pay, father_name, loan_number, jr_letter_date, jr_letter_number,
                        screening_date, ro_date, pso_date, ro_number, post_pso_ref, bank_district, cheque_date):

        if pso_date:
            pso_date = (datetime.combine(datetime.strptime(pso_date, '%Y-%m-%d').date(),
                                         datetime.now().time()))
        else:
            pso_date = pso_date

        if cheque_date:
            cheque_date = (datetime.combine(datetime.strptime(cheque_date, '%Y-%m-%d').date(),
                                            datetime.now().time()))
        else:
            cheque_date = cheque_date

        if ro_date:
            ro_date = (datetime.combine(datetime.strptime(ro_date, '%Y-%m-%d').date(),
                                        datetime.now().time()))
        else:
            ro_date = ro_date

        if received_date:
            received_date = (datetime.combine(datetime.strptime(received_date, '%Y-%m-%d').date(),
                                              datetime.now().time()))
        else:
            received_date = received_date

        if screening_date:
            screening_date = (datetime.combine(datetime.strptime(screening_date, '%Y-%m-%d').date(),
                                               datetime.now().time()))
        else:
            screening_date = screening_date

        if jr_letter_date:
            jr_letter_date = (datetime.combine(datetime.strptime(jr_letter_date, '%Y-%m-%d').date(),
                                               datetime.now().time()))
        else:
            jr_letter_date = jr_letter_date

        if status_date:
            status_date = (datetime.combine(datetime.strptime(status_date, '%Y-%m-%d').date(),
                                            datetime.now().time()))
        else:
            status_date = status_date

        Database.update_application(collection='loans', query={'_id': loan_id}, applicant_name=applicant_name,
                                    loan_category=loan_category, age=age, gender=gender, address=address, roi=roi,
                                    district=district, annual_income=annual_income, caste=caste, bank=bank, sb=sub_bank,
                                    no_of_demands=no_of_demands, loan_reason=loan_reason, loan_amount=loan_amount,
                                    received_date=received_date, status=status, status_date=status_date,
                                    ann_loan_id=ann_loan_id, user_id=user_id, user_name=user_name, shg_name=shg_name,
                                    amount_per_member=amount_per_member, strength=strength, no_of_shgs=no_of_shgs,
                                    cheque_number=cheque_number, amount_to_pay=amount_to_pay, father_name=father_name,
                                    loan_number=loan_number, jr_letter_date=jr_letter_date,
                                    jr_letter_number=jr_letter_number, screening_date=screening_date, ro_date=ro_date,
                                    pso_date=pso_date, ro_number=ro_number, post_pso_ref=post_pso_ref,
                                    bank_district=bank_district, cheque_date=cheque_date)

    @classmethod
    def update_pend_amount(cls, amount_yet_to_be_paid, loan_id):
        Database.update_pending_amount(collection='loans', query={'ann_loan_id': loan_id},
                                       amount_yet_to_be_paid=amount_yet_to_be_paid)

    @classmethod
    def deletefrom_mongo(cls, _id):
        Database.delete_from_mongo(collection='loans', query={'_id': _id})

    def json(self):
        return {
            'applicant_name': self.applicant_name,
            'father_name': self.father_name,
            'loan_category': self.loan_category,
            'age': self.age,
            'gender': self.gender,
            'address': self.address,
            'district': self.district,
            'bank_district': self.bank_district,
            'caste': self.caste,
            'annual_income': self.annual_income,
            'bank': self.bank,
            'sub_bank': self.sub_bank,
            'loan_reason': self.loan_reason,
            'received_date': self.received_date,
            'screening_date': self.screening_date,
            'status': self.status,
            'status_date': self.status_date,
            'jr_letter_date': self.jr_letter_date,
            'jr_letter_number': self.jr_letter_number,
            'ann_loan_id': self.ann_loan_id,
            'loan_amount': self.loan_amount,
            'loan_number': self.loan_number,
            'amount_yet_to_pay': self.amount_yet_to_pay,
            'final_collection_amount': self.final_collection_amount,
            'roi': self.roi,
            'no_of_demands': self.no_of_demands,
            'user_name': self.user_name,
            'user_id': self.user_id,
            'no_of_shgs': self.no_of_shgs,
            'strength': self.strength,
            'amount_per_member': self.amount_per_member,
            'shg_name': self.shg_name,
            'total_amount': self.total_amount,
            'cheque_number': self.cheque_number,
            'ro_date': self.ro_date,
            'ro_number': self.ro_number,
            'pso_date': self.pso_date,
            'post_pso_ref_no': self.post_pso_ref_no,
            '_id': self._id,
        }

    @classmethod
    def get_by_id(cls, _id):
        data = Database.find('loans', {'_id': _id})
        return [cls(**data) for data in data]
