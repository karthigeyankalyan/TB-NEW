from datetime import datetime

import pymongo
from bson import json_util
from flask import Flask, render_template, request, session, json, abort
from src.common.database import Database
from src.models.accounts import Account
from src.models.loan_financials import Demand
from src.models.loanapplication import LoanApplication
from src.models.user import User

app = Flask(__name__)  # main
app.secret_key = "commercial"


@app.before_first_request
def initialize_database():
    Database.initialize()


@app.route('/')
def home():
    # remote_address = request.headers.getlist("X-Forwarded-For")[0]
    return render_template('home.html')


@app.route('/login')
def login_form():
    return render_template('login.html')


@app.route('/register')
def register_form():
    return render_template('register.html')


@app.route('/profile_landing')
def profile():
    email = session['email']
    user = User.get_by_email(email)

    if email:
        if user.department == 'Accounts':
            return render_template('profile_accounts.html', user=user)
        elif user.department == 'Loans':
            return render_template('profile_loans.html', user=user)
        else:
            return render_template('profile_HQ.html', user=user)

    else:
        return render_template('login_fail.html')


@app.route('/authorize/login', methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']
    valid = User.valid_login(email, password)
    User.login(email)
    user = User.get_by_email(email)

    if valid:
        if user.department == 'Accounts':
            return render_template('profile_accounts.html', user=user)
        elif user.department == 'Loans':
            return render_template('profile_loans.html', user=user)
        else:
            return render_template('profile_HQ.html', user=user)

    else:
        return render_template('login_fail.html')


@app.route('/authorize/register', methods=['POST'])
def register_user():
    email = request.form['email']
    password = request.form['password']
    username = request.form['username']
    designation = request.form['designation']
    department = request.form['department']

    User.register(email, password, username, designation, department)

    user = User.get_by_email(email)

    if user.department == 'Accounts':
        return render_template('profile_accounts.html', user=user)
    elif user.department == 'Loans':
        return render_template('profile_loans.html', user=user)
    else:
        return render_template('profile_HQ.html', user=user)


@app.route('/new_receipt/<string:user_id>', methods=['POST', 'GET'])
def receipt_form(user_id):
    email = session['email']
    if email is not None:
        if request.method == 'GET':
            user = User.get_by_id(user_id)
            return render_template('receipt_form.html', user=user)

        else:
            user = User.get_by_id(user_id)
            invoice_date = request.form['invoiceDate']
            voucher_date = request.form['voucherDate']
            adjustmentVoucher = request.form['adjustmentVoucher']
            ledger = request.form['ledger']
            nature_of_transaction = request.form['natureOfTransaction']
            account_head = request.form['accountHead']
            bank_account = request.form['bankAccount']
            amount = request.form['amount']
            narration = request.form['narration']
            cheque_num = request.form['cheque']
            pvoucher = request.form['paymentVoucher']
            depoBank = request.form['depositingBank']
            cheque_date = request.form['chequeDate']
            user_id = user_id
            user_name = user.username

            doc_account_dict = {"LOAN FROM NBCFDC (GTL)": "Borrowings from NBCFDC",
                                "LOAN FROM NBCFDC (MCS)": "Borrowings from NBCFDC",
                                "LOAN FROM NBCFDC (MSY)": "Borrowings from NBCFDC",
                                "BANK OF BARODA , MOUNT ROAD BR": "Cash and Cash Equivalents",
                                "FIXED DEPOSIT": "Cash and Cash Equivalents",
                                "Indian Bank T.Nagar Branch": "Cash and Cash Equivalents",
                                "INDUSIND BANK, NUNGABAKKAM BR": "Cash and Cash Equivalents",
                                "IOB, MOUNT ROAD": "Cash and Cash Equivalents",
                                "Karur Vysya Bank Kodambakkam branch": "Cash and Cash Equivalents",
                                "P.D. A/C - RBI": "Cash and Cash Equivalents",
                                "STAMPS ON HAND": "Cash and Cash Equivalents",
                                "SYNDICATE BANK, EGMORE BR": "Cash and Cash Equivalents",
                                "TAMILNADU STATE APEX CO-OP BANK": "Cash and Cash Equivalents",
                                "DEPRECIATION": "Depreciation",
                                "BOOKS & PERIODICALS": "Employee Benefit Expenses",
                                "CONTRIBUTION TO EPF & OTHER FUNDS": "Employee Benefit Expenses",
                                "GROUP INSURANCE SCHEME": "Employee Benefit Expenses",
                                "MEDICAL EXPENSES": "Employee Benefit Expenses",
                                "NEW HEALTH INSURANCE SCHEME": "Employee Benefit Expenses",
                                "PENSION CONTRIBUTION": "Employee Benefit Expenses",
                                "SALARIES": "Employee Benefit Expenses",
                                "VEHICLE HIRE CHARGES": "Employee Benefit Expenses",
                                "GUARANTEE COMMISSION TO T.N. GOVT.": "Finance Cost",
                                "INTEREST PAID TO NBCFDC": "Finance Cost",
                                "PROVISION FOR GRATUITY": "Long Term Provisions",
                                "PROVISION FOR LEAVE SALARY": "Long Term Provisions",
                                "WORK IN PROGRESS": "Capital Work-In Progress",
                                "ADVANCE TO TUCS LTD.": "Other Current Assets",
                                "ADVANCE-NEW CATHEDRAL SERVICE STATION": "Other Current Assets",
                                "ADVANCES": "Other Current Assets",
                                "AMOUNT DUE FROM CTA": "Other Current Assets",
                                "AMOUNT RECEIVABLE FROM ELCOT": "Other Current Assets",
                                "AMOUNT RECEIVABLE FROM NBCFDC": "Other Current Assets",
                                "FESTIVAL ADVANCE": "Other Current Assets",
                                "INTEREST ACCURED BUT NOT DUE ON FD": "Other Current Assets",
                                "INTERIM ARREARS": "Other Current Assets",
                                "TELEPHONE DEPOSIT": "Other Current Assets",
                                "AMOUNT PAYABLE TO TAMCO (CAR)": "Other Current Liabilities",
                                "AMOUNT RECEIVED FROM GOVT (IRRI)": "Other Current Liabilities",
                                "AMT REC FROM NBCFDC FOR EXHIBITION": "Other Current Liabilities",
                                "AMT REVD FROM GOVT - JOT (PD A/c)": "Other Current Liabilities",
                                "ARREARS PAYABLE": "Other Current Liabilities",
                                "CANCELLATION OF CHEQUE(JOT)": "Other Current Liabilities",
                                "COMPUTER TRAINING": "Other Current Liabilities",
                                "GUARANTEE COMMISSIN PAYABLE TO TN GOVT": "Other Current Liabilities",
                                "MARGIN ON INTEREST PAYABLE TO SCAS (SC)": "Other Current Liabilities",
                                "OUTSTANDING EXPENSES": "Other Current Liabilities",
                                "SUBSIDY RECEIVED FROM GOVT FOR ML": "Other Current Liabilities",
                                "TAICO INT": "Other Current Liabilities",
                                "TAMCO": "Other Current Liabilities",
                                "TRAINING GRANT IN AID FROM NBCFDC": "Other Current Liabilities",
                                "BAD AND DOUBTFUL DEBTS": "Other Expenses",
                                "BANK CHARGES": "Other Expenses",
                                "BOARD MEETING EXPENSE": "Other Expenses",
                                "COMPUTERS": "Other Expenses",
                                "CONVEYANCE CHARGES": "Other Expenses",
                                "COST OF FUEL": "Other Expenses",
                                "ELECTRICITY CHARGES": "Other Expenses",
                                "EXHIBITION/ADVERTISEMENT EXEPNSES": "Other Expenses",
                                "FILING FEES": "Other Expenses",
                                "INSURANCE": "Other Expenses",
                                "INTERNAL AUDIT FEES PAYABLE": "Other Expenses",
                                "STATUTORY AUDIT FEES PAYABLE": "Other Expenses",
                                "INTERNAL AUDIT FEES": "Other Expenses",
                                "LEGAL FEES": "Other Expenses",
                                "MEETING EXPENSE": "Other Expenses",
                                "OFFICE EQUIPMENT": "Other Expenses",
                                "OFFICE EXPENSE": "Other Expenses",
                                "PETTY CASH": "Other Expenses",
                                "POSTAGE EXPENSES": "Other Expenses",
                                "PRINTING & STATIONERY": "Other Expenses",
                                "PROFEESIONAL FEES": "Other Expenses",
                                "Purchase of Telephone": "Other Expenses",
                                "REFRESHMENT CHARGES": "Other Expenses",
                                "REMUNERATION TO CHARMAN": "Other Expenses",
                                "RENT": "Other Expenses",
                                "REPAIR & MAINTENANCE": "Other Expenses",
                                "SERVICE CHARGES": "Other Expenses",
                                "SOFTWARE DEVELOPMENT ": "Other Expenses",
                                "STATUTORY AUDIT FEES": "Other Expenses",
                                "TAX AUDIT FEES": "Other Expenses",
                                "TELEPHONE CHARGES": "Other Expenses",
                                "TRAVELLING EXPENSE/TTA": "Other Expenses",
                                "VEHICLE MAINTANCE": "Other Expenses",
                                "WAGES": "Other Expenses",
                                "COMM OF BACKWARD CLASSES": "Other Income",
                                "GRATUITY": "Other Income",
                                "Gain on sale of assets": "Other Income",
                                "INTEREST ACCRUED ON FD": "Other Income",
                                "INTEREST ACCRUED ON SB A/C": "Other Income",
                                "INTEREST FROM TAMCO receivable": "Other Income",
                                "INTEREST ON FIXED DEPOSIT": "Other Income",
                                "INTEREST ON SAVING BANK A/C": "Other Income",
                                "Sale of Tender Form": "Other Income",
                                "INTEREST ACCRUED ON ML LOAN": "Other Non-Current Assets",
                                "PENAL INTEREST ACCRUED": "Other Non-Current Assets",
                                "LOAN HOSTEL -PRINCIPAL": "Principal Lent",
                                "LOAN TO AAVIN-PRINCIPAL": "Principal Lent",
                                "LOAN TO DCCB (GTL) - PRINCIPAL": "Principal Lent",
                                "LOAN TO EDP TRAINED WOMEN - PRINCIPAL": "Principal Lent",
                                "LOAN TO HDC-PRINCIPAL": "Principal Lent",
                                "LOAN TO ICS (AUTO)-PRINCIPAL (BC)": "Principal Lent",
                                "LOAN TO ICS (AUTO)-PRINCIPAL (G)": "Principal Lent",
                                "LOAN TO ICS (AUTO)-PRINCIPAL (M)": "Principal Lent",
                                "LOAN TO ICS (MML) PRINCIPAL": "Principal Lent",
                                "LOAN TO MICRO CREDIT SCHEME-PRINCIPAL": "Principal Lent",
                                "LOAN TO NSS -PRINCIPAL": "Principal Lent",
                                "LOAN TO PACB (GTL) - PRINCIPAL": "Principal Lent",
                                "LOAN TO SUGAR MILL-PRINCIPAL": "Principal Lent",
                                "LOAN TO TAICO-PRINCIPAL": "Principal Lent",
                                "LOAN TO UCB (GTL) -PRINCIPAL": "Principal Lent",
                                "DCCB INT": "Revenue From Operations",
                                "DCCB P.INT": "Revenue From Operations",
                                "EDP INTEREST": "Revenue From Operations",
                                "EDP P INT.": "Revenue From Operations",
                                "INTEREST ON ML LOAN": "Revenue From Operations",
                                "MAS INT.": "Revenue From Operations",
                                "MAS P.INT": "Revenue From Operations",
                                "MICRO CREDIT SCHEME INT": "Revenue From Operations",
                                "MICRO CREDIT SCHEME P.INT": "Revenue From Operations",
                                "MLL INT.": "Revenue From Operations",
                                "MLL P.INT": "Revenue From Operations",
                                "NSS INTEREST": "Revenue From Operations",
                                "NSS P.INTEREST": "Revenue From Operations",
                                "PACB INT": "Revenue From Operations",
                                "PACB P.INT": "Revenue From Operations",
                                "UCB INT": "Revenue From Operations",
                                "UCB P.INT": "Revenue From Operations",
                                "ISSUED, SUBSCRIBED AND PAID-UP": "Share Capital",
                                "PROVISION FOR BONUS": "Short Term Provisions",
                                "AMOUNT TRANSFERRED TO TAMCO": "NA",
                                "BONUS": "NA",
                                "Buildings": "NA",
                                "FURNITURE & FITTINGS": "NA",
                                "LEAVE SALARY": "NA",
                                "LOAN FOR SETTING UP OF MOBILE LAUNDRY": "NA",
                                "MOTOR CAR": "NA",
                                "PROFIT AND LOSS ACCOUNT": "NA",
                                "PROVISION FOR BAD & DOUDTFUL DEBTIS": "NA",
                                "STIPEND": "NA",
                                "SUBSIDY CHARGES RECEIVABLE FROM GOVT.": "NA",
                                "TDS ON BANK DEPOSITS": "NA",
                                "TDS ON RENT": "NA"}

            doc_account_head = doc_account_dict[account_head]

            account = Account(invoice_date=invoice_date, nature_of_transaction=nature_of_transaction,
                              account_head=account_head, bank_account=bank_account, amount=amount,
                              user_id=user_id, user_name=user_name, doc_account_head=doc_account_head,
                              cheque_number=cheque_num, payment_voucher=pvoucher, depositing_bank=depoBank,
                              voucher_date=voucher_date, adjustment_voucher=adjustmentVoucher,
                              ledger=ledger, cleared="No", cheque_date=cheque_date, narration=narration)

            account.save_to_mongo()

            return render_template('receipt_added.html', account=account, user=user)

    else:
        return render_template('login_fail.html')


@app.route('/updateReceipt/<string:_id>', methods=['POST', 'GET'])
def update_receipt(_id):
    email = session['email']
    if email is not None:
        if request.method == 'GET':
            user = User.get_by_email(email)
            return render_template('update_receipt_form.html', user=user, receipt_id=_id)

        else:
            user = User.get_by_email(email)
            invoice_date = request.form['invoiceDate']
            voucher_date = request.form['voucherDate']
            adjustmentVoucher = request.form['adjustmentVoucher']
            ledger = request.form['ledger']
            nature_of_transaction = request.form['natureOfTransaction']
            account_head = request.form['accountHead']
            bank_account = request.form['bankAccount']
            amount = request.form['amount']
            narration = request.form['narration']
            cheque_num = request.form['cheque']
            pvoucher = request.form['paymentVoucher']
            depoBank = request.form['depositingBank']
            cleared = request.form['cleared']
            cheque_date = request.form['chequeDate']
            user_id = user._id
            user_name = user.username

            doc_account_dict = {"LOAN FROM NBCFDC (GTL)": "Borrowings from NBCFDC",
                                "LOAN FROM NBCFDC (MCS)": "Borrowings from NBCFDC",
                                "LOAN FROM NBCFDC (MSY)": "Borrowings from NBCFDC",
                                "BANK OF BARODA , MOUNT ROAD BR": "Cash and Cash Equivalents",
                                "FIXED DEPOSIT": "Cash and Cash Equivalents",
                                "Indian Bank T.Nagar Branch": "Cash and Cash Equivalents",
                                "INDUSIND BANK, NUNGABAKKAM BR": "Cash and Cash Equivalents",
                                "IOB, MOUNT ROAD": "Cash and Cash Equivalents",
                                "Karur Vysya Bank Kodambakkam branch": "Cash and Cash Equivalents",
                                "P.D. A/C - RBI": "Cash and Cash Equivalents",
                                "STAMPS ON HAND": "Cash and Cash Equivalents",
                                "SYNDICATE BANK, EGMORE BR": "Cash and Cash Equivalents",
                                "TAMILNADU STATE APEX CO-OP BANK": "Cash and Cash Equivalents",
                                "DEPRECIATION": "Depreciation",
                                "BOOKS & PERIODICALS": "Employee Benefit Expenses",
                                "CONTRIBUTION TO EPF & OTHER FUNDS": "Employee Benefit Expenses",
                                "GROUP INSURANCE SCHEME": "Employee Benefit Expenses",
                                "MEDICAL EXPENSES": "Employee Benefit Expenses",
                                "NEW HEALTH INSURANCE SCHEME": "Employee Benefit Expenses",
                                "PENSION CONTRIBUTION": "Employee Benefit Expenses",
                                "SALARIES": "Employee Benefit Expenses",
                                "VEHICLE HIRE CHARGES": "Employee Benefit Expenses",
                                "GUARANTEE COMMISSION TO T.N. GOVT.": "Finance Cost",
                                "INTEREST PAID TO NBCFDC": "Finance Cost",
                                "PROVISION FOR GRATUITY": "Long Term Provisions",
                                "PROVISION FOR LEAVE SALARY": "Long Term Provisions",
                                "WORK IN PROGRESS": "Non-Current Assets",
                                "ADVANCE TO TUCS LTD.": "Other Current Assets",
                                "ADVANCE-NEW CATHEDRAL SERVICE STATION": "Other Current Assets",
                                "ADVANCES": "Other Current Assets",
                                "AMOUNT DUE FROM CTA": "Other Current Assets",
                                "AMOUNT RECEIVABLE FROM ELCOT": "Other Current Assets",
                                "AMOUNT RECEIVABLE FROM NBCFDC": "Other Current Assets",
                                "FESTIVAL ADVANCE": "Other Current Assets",
                                "INTEREST ACCURED BUT NOT DUE ON FD": "Other Current Assets",
                                "INTERIM ARREARS": "Other Current Assets",
                                "TELEPHONE DEPOSIT": "Other Current Assets",
                                "AMOUNT PAYABLE TO TAMCO (CAR)": "Other Current Liabilities",
                                "AMOUNT RECEIVED FROM GOVT (IRRI)": "Other Current Liabilities",
                                "AMT REC FROM NBCFDC FOR EXHIBITION": "Other Current Liabilities",
                                "AMT REVD FROM GOVT - JOT (PD A/c)": "Other Current Liabilities",
                                "ARREARS PAYABLE": "Other Current Liabilities",
                                "CANCELLATION OF CHEQUE(JOT)": "Other Current Liabilities",
                                "COMPUTER TRAINING": "Other Current Liabilities",
                                "GUARANTEE COMMISSIN PAYABLE TO TN GOVT": "Other Current Liabilities",
                                "MARGIN ON INTEREST PAYABLE TO SCAS (SC)": "Other Current Liabilities",
                                "OUTSTANDING EXPENSES": "Other Current Liabilities",
                                "SUBSIDY RECEIVED FROM GOVT FOR ML": "Other Current Liabilities",
                                "TAICO INT": "Other Current Liabilities",
                                "TAMCO": "Other Current Liabilities",
                                "TRAINING GRANT IN AID FROM NBCFDC": "Other Current Liabilities",
                                "BAD AND DOUBTFUL DEBTS": "Other Expenses",
                                "BANK CHARGES": "Other Expenses",
                                "BOARD MEETING EXPENSE": "Other Expenses",
                                "COMPUTERS": "Other Expenses",
                                "CONVEYANCE CHARGES": "Other Expenses",
                                "COST OF FUEL": "Other Expenses",
                                "ELECTRICITY CHARGES": "Other Expenses",
                                "EXHIBITION/ADVERTISEMENT EXEPNSES": "Other Expenses",
                                "FILING FEES": "Other Expenses",
                                "INSURANCE": "Other Expenses",
                                "INTERNAL AUDIT FEES PAYABLE": "Other Expenses",
                                "STATUTORY AUDIT FEES PAYABLE": "Other Expenses",
                                "INTERNAL AUDIT FEES": "Other Expenses",
                                "LEGAL FEES": "Other Expenses",
                                "MEETING EXPENSE": "Other Expenses",
                                "OFFICE EQUIPMENT": "Other Expenses",
                                "OFFICE EXPENSE": "Other Expenses",
                                "PETTY CASH": "Other Expenses",
                                "POSTAGE EXPENSES": "Other Expenses",
                                "PRINTING & STATIONERY": "Other Expenses",
                                "PROFEESIONAL FEES": "Other Expenses",
                                "Purchase of Telephone": "Other Expenses",
                                "REFRESHMENT CHARGES": "Other Expenses",
                                "REMUNERATION TO CHARMAN": "Other Expenses",
                                "RENT": "Other Expenses",
                                "REPAIR & MAINTENANCE": "Other Expenses",
                                "SERVICE CHARGES": "Other Expenses",
                                "SOFTWARE DEVELOPMENT ": "Other Expenses",
                                "STATUTORY AUDIT FEES": "Other Expenses",
                                "TAX AUDIT FEES": "Other Expenses",
                                "TELEPHONE CHARGES": "Other Expenses",
                                "TRAVELLING EXPENSE/TTA": "Other Expenses",
                                "VEHICLE MAINTANCE": "Other Expenses",
                                "WAGES": "Other Expenses",
                                "COMM OF BACKWARD CLASSES": "Other Income",
                                "GRATUITY": "Other Income",
                                "Gain on sale of assets": "Other Income",
                                "INTEREST ACCRUED ON FD": "Other Income",
                                "INTEREST ACCRUED ON SB A/C": "Other Income",
                                "INTEREST FROM TAMCO receivable": "Other Income",
                                "INTEREST ON FIXED DEPOSIT": "Other Income",
                                "INTEREST ON SAVING BANK A/C": "Other Income",
                                "Sale of Tender Form": "Other Income",
                                "INTEREST ACCRUED ON ML LOAN": "Other Non-Current Assets",
                                "PENAL INTEREST ACCRUED": "Other Non-Current Assets",
                                "LOAN HOSTEL -PRINCIPAL": "Principal Lent",
                                "LOAN TO AAVIN-PRINCIPAL": "Principal Lent",
                                "LOAN TO DCCB (GTL) - PRINCIPAL": "Principal Lent",
                                "LOAN TO EDP TRAINED WOMEN - PRINCIPAL": "Principal Lent",
                                "LOAN TO HDC-PRINCIPAL": "Principal Lent",
                                "LOAN TO ICS (AUTO)-PRINCIPAL (BC)": "Principal Lent",
                                "LOAN TO ICS (AUTO)-PRINCIPAL (G)": "Principal Lent",
                                "LOAN TO ICS (AUTO)-PRINCIPAL (M)": "Principal Lent",
                                "LOAN TO ICS (MML) PRINCIPAL": "Principal Lent",
                                "LOAN TO MICRO CREDIT SCHEME-PRINCIPAL": "Principal Lent",
                                "LOAN TO NSS -PRINCIPAL": "Principal Lent",
                                "LOAN TO PACB (GTL) - PRINCIPAL": "Principal Lent",
                                "LOAN TO SUGAR MILL-PRINCIPAL": "Principal Lent",
                                "LOAN TO TAICO-PRINCIPAL": "Principal Lent",
                                "LOAN TO UCB (GTL) -PRINCIPAL": "Principal Lent",
                                "DCCB INT": "Revenue From Operations",
                                "DCCB P.INT": "Revenue From Operations",
                                "EDP INTEREST": "Revenue From Operations",
                                "EDP P INT.": "Revenue From Operations",
                                "INTEREST ON ML LOAN": "Revenue From Operations",
                                "MAS INT.": "Revenue From Operations",
                                "MAS P.INT": "Revenue From Operations",
                                "MICRO CREDIT SCHEME INT": "Revenue From Operations",
                                "MICRO CREDIT SCHEME P.INT": "Revenue From Operations",
                                "MLL INT.": "Revenue From Operations",
                                "MLL P.INT": "Revenue From Operations",
                                "NSS INTEREST": "Revenue From Operations",
                                "NSS P.INTEREST": "Revenue From Operations",
                                "PACB INT": "Revenue From Operations",
                                "PACB P.INT": "Revenue From Operations",
                                "UCB INT": "Revenue From Operations",
                                "UCB P.INT": "Revenue From Operations",
                                "ISSUED, SUBSCRIBED AND PAID-UP": "Share Capital",
                                "PROVISION FOR BONUS": "Short Term Provisions",
                                "AMOUNT TRANSFERRED TO TAMCO": "NA",
                                "BONUS": "NA",
                                "Buildings": "NA",
                                "FURNITURE & FITTINGS": "NA",
                                "LEAVE SALARY": "NA",
                                "LOAN FOR SETTING UP OF MOBILE LAUNDRY": "NA",
                                "MOTOR CAR": "NA",
                                "PROFIT AND LOSS ACCOUNT": "NA",
                                "PROVISION FOR BAD & DOUDTFUL DEBTIS": "NA",
                                "STIPEND": "NA",
                                "SUBSIDY CHARGES RECEIVABLE FROM GOVT.": "NA",
                                "TDS ON BANK DEPOSITS": "NA",
                                "TDS ON RENT": "NA"}

            doc_account_head = doc_account_dict[account_head]

            invoice_date = datetime.combine(datetime.strptime(invoice_date, '%Y-%m-%d').date(),
                                            datetime.now().time())
            cheque_date = datetime.combine(datetime.strptime(cheque_date, '%Y-%m-%d').date(),
                                           datetime.now().time())
            voucher_date = datetime.combine(datetime.strptime(voucher_date, '%Y-%m-%d').date(),
                                            datetime.now().time())

            Account.update_receipt(invoice_date=invoice_date, nature_of_transaction=nature_of_transaction,
                                   account_head=account_head, bank_account=bank_account, amount=amount,
                                   user_id=user_id, user_name=user_name, doc_account_head=doc_account_head, _id=_id,
                                   payment_voucher=pvoucher, cheque_number=cheque_num, depositing_bank=depoBank,
                                   adjustment_voucher=adjustmentVoucher, voucher_date=voucher_date, ledger=ledger,
                                   cleared=cleared, cheque_date=cheque_date, narration=narration)

            return render_template('application_added.html', user=user)

    else:
        return render_template('login_fail.html')


@app.route('/new_loanApplication/<string:user_id>', methods=['POST', 'GET'])
def loan_form(user_id):
    email = session['email']
    if email is not None:
        if request.method == 'GET':
            user = User.get_by_id(user_id)
            return render_template('loan_app_form.html', user=user)

        else:
            category = request.form['loanCategory']
            if category == "GTL (General Term Loan)" or category == "NSS (New-Swarnima Scheme)":
                user = User.get_by_id(user_id)
                applicant_name = request.form['applicantName']
                applicant_father_name = request.form['applicantFatherName']
                loan_category = request.form['loanCategory']
                age = request.form['age']
                gender = request.form['gender']
                address = request.form['address']
                district = request.form['district']
                bank_district = request.form['bankDistrict']
                annual_income = request.form['annualIncome']
                caste = request.form['caste']
                bank = request.form['bankName']
                sub_bank = request.form['subBank']
                loan_reason = request.form['loanReason']
                loan_amount = request.form['loanAmount']
                loanNumber = request.form['loanNumber']
                received_date = request.form['receivedDate']
                screening_date = request.form['screeningDate']
                roi = request.form['interest']
                no_of_demands = request.form['noOfDemands']
                status = request.form['status']
                status_date = request.form['statusDate']
                jr_letter_date = request.form['jrLetterDate']
                jr_letter_number = request.form['jrLetterNumber']
                ann_loan_id = request.form['annualLoanID']
                no_of_shgs = request.form['shgCount']
                user_id = user_id
                user_name = user.username
                cheque_number = request.form['chequeNumber']
                pso_date = request.form['psoDate']
                ro_ref = request.form['roRef']
                ro_date = request.form['roDate']

                application = LoanApplication(applicant_name=applicant_name, loan_category=loan_category, age=age,
                                              gender=gender, address=address, district=district,
                                              annual_income=annual_income, caste=caste, bank=bank,
                                              loan_reason=loan_reason, loan_amount=loan_amount,
                                              received_date=received_date, status=status,
                                              status_date=status_date, ann_loan_id=ann_loan_id, user_id=user_id,
                                              user_name=user_name, no_of_shgs=no_of_shgs, cheque_number=cheque_number,
                                              sub_bank=sub_bank, roi=roi, no_of_demands=no_of_demands,
                                              father_name=applicant_father_name, screening_date=screening_date,
                                              loan_number=loanNumber, jr_letter_date=jr_letter_date,
                                              jr_letter_number=jr_letter_number, pso_date=pso_date,
                                              ro_date=ro_date, post_pso_ref_no=ro_ref)

                application.save_to_mongo()

                return render_template('application_added.html', application=application, user=user)

            else:
                user = User.get_by_id(user_id)
                applicant_name = request.form['applicantName']
                applicant_father_name = request.form['applicantFatherName']
                loan_category = request.form['loanCategory']
                age = request.form['age']
                gender = request.form['gender']
                address = request.form['address']
                district = request.form['district']
                bank_district = request.form['bankDistrict']
                annual_income = request.form['annualIncome']
                caste = request.form['caste']
                bank = request.form['bankName']
                sub_bank = request.form['subBank']
                loan_reason = request.form['loanReason']
                loanNumber = request.form['loanNumber']
                total_loan_amount = request.form['loanAmount']
                received_date = request.form['receivedDate']
                screening_date = request.form['screeningDate']
                roi = request.form['interest']
                no_of_demands = request.form['noOfDemands']
                status = request.form['status']
                status_date = request.form['statusDate']
                jr_letter_date = request.form['jrLetterDate']
                jr_letter_number = request.form['jrLetterNumber']
                ann_loan_id = request.form['annualLoanID']
                no_of_shgs = int(request.form['shgCount'])
                inv_id = int(request.form['invIDCTR'])
                user_id = user_id
                user_name = user.username
                cheque_number = request.form['chequeNumber']
                ro_date = request.form['roDate']
                ro_number = request.form['roNumber']
                ro_ref = request.form['roRef']

                for i in range(int(inv_id)):
                    print(inv_id)
                    shg_name_string = "sn" + str(i)
                    amount_per_member_string = "apm" + str(i)
                    strength_string = "strength" + str(i)
                    ta = "ta" + str(i)
                    sb = "sb" + str(i)
                    shg_name = request.form[shg_name_string]
                    amount_per_member = request.form[amount_per_member_string]
                    strength = request.form[strength_string]
                    sub_bank = request.form[sb]

                    application = LoanApplication(applicant_name=applicant_name, loan_category=loan_category, age=age,
                                                  gender=gender, address=address, district=district,
                                                  annual_income=annual_income, caste=caste, bank=bank,
                                                  loan_reason=loan_reason, loan_amount=total_loan_amount,
                                                  received_date=received_date, status=status,
                                                  status_date=status_date, ann_loan_id=ann_loan_id, user_id=user_id,
                                                  user_name=user_name, no_of_shgs=no_of_shgs,
                                                  cheque_number=cheque_number, sub_bank=sub_bank, roi=roi,
                                                  no_of_demands=no_of_demands, father_name=applicant_father_name,
                                                  screening_date=screening_date, loan_number=loanNumber,
                                                  jr_letter_date=jr_letter_date, jr_letter_number=jr_letter_number,
                                                  shg_name=shg_name, amount_per_member=amount_per_member,
                                                  strength=strength, ro_date=ro_date, ro_number=ro_number,
                                                  post_pso_ref_no=ro_ref, bank_district=bank_district)

                    application.save_to_mongo()

                return render_template('application_addedv2.html', user=user)

    else:
        return render_template('login_fail.html')


@app.route('/addAnotherApplication/<string:_id>', methods=['POST', 'GET'])
def add_another_loan_form(_id):
    email = session['email']
    if email is not None:
        if request.method == 'GET':
            user = User.get_by_email(email)
            return render_template('another_loan_app_form.html', user=user, application_id=_id)

        else:
            user = User.get_by_email(email)
            applicant_name = request.form['applicantName']
            applicant_father_name = request.form['applicantFatherName']
            loan_category = request.form['loanCategory']
            age = request.form['age']
            gender = request.form['gender']
            address = request.form['address']
            district = request.form['district']
            bank_district = request.form['bankDistrict']
            annual_income = request.form['annualIncome']
            caste = request.form['caste']
            bank = request.form['bankName']
            sub_bank = request.form['subBank']
            loan_reason = request.form['loanReason']
            loan_amount = request.form['loanAmount']
            loanNumber = request.form['loanNumber']
            received_date = request.form['receivedDate']
            screening_date = request.form['screeningDate']
            roi = request.form['interest']
            no_of_demands = request.form['noOfDemands']
            status = request.form['status']
            status_date = request.form['statusDate']
            jr_letter_date = request.form['jrLetterDate']
            jr_letter_number = request.form['jrLetterNumber']
            ann_loan_id = request.form['annualLoanID']
            no_of_shgs = request.form['shgCount']
            user_id = user._id
            user_name = user.username
            no_of_beneficiaries = request.form['beneficiaryCount']
            cheque_number = request.form['chequeNumber']
            ro_ref = request.form['roRef']

            application = LoanApplication(applicant_name=applicant_name, loan_category=loan_category, age=age,
                                          gender=gender, address=address, district=district,
                                          annual_income=annual_income, caste=caste, bank=bank, loan_reason=loan_reason,
                                          loan_amount=loan_amount, received_date=received_date, status=status,
                                          status_date=status_date, ann_loan_id=ann_loan_id, user_id=user_id,
                                          user_name=user_name, cheque_number=cheque_number,
                                          sub_bank=sub_bank, roi=roi, no_of_demands=no_of_demands,
                                          father_name=applicant_father_name, screening_date=screening_date,
                                          loan_number=loanNumber, jr_letter_date=jr_letter_date,
                                          jr_letter_number=jr_letter_number, post_pso_ref_no=ro_ref,
                                          bank_district=bank_district)

            application.save_to_mongo()

            return render_template('application_added.html', application=application, user=user)

    else:
        return render_template('login_fail.html')


@app.route('/updateApplication/<string:_id>', methods=['POST', 'GET'])
def update_loan_form(_id):
    email = session['email']
    if email is not None:
        if request.method == 'GET':

            application = Database.find("loans", {"_id": _id})

            annual_loan_id, loan_category = None, None

            for result_object in application[0:1]:
                loan_category = result_object['loan_category']
                annual_loan_id = result_object['ann_loan_id']

            user = User.get_by_email(email)

            if loan_category == "GTL (General Term Loan)" or loan_category == "NSS (New-Swarnima Scheme)":
                return render_template('update_loan_app_form.html', user=user, application_id=_id)
            else:
                return render_template('shg_update_loan_app_form.html', user=user, application_id=_id,
                                       annual_loan_id=annual_loan_id)

        else:
            application = Database.find("loans", {"_id": _id})

            annual_loan_id, loan_category = None, None

            for result_object in application[0:1]:
                loan_category = result_object['loan_category']
                annual_loan_id = result_object['ann_loan_id']
                amount_to_pay = result_object['amount_yet_to_pay']

            if loan_category == "GTL (General Term Loan)" or loan_category == "NSS (New-Swarnima Scheme)":
                user = User.get_by_email(email)
                applicant_name = request.form['applicantName']
                applicant_father_name = request.form['applicantFatherName']
                loan_category = request.form['loanCategory']
                age = request.form['age']
                gender = request.form['gender']
                address = request.form['address']
                district = request.form['district']
                bank_district = request.form['bankDistrict']
                annual_income = request.form['annualIncome']
                caste = request.form['caste']
                bank = request.form['bankName']
                sub_bank = request.form['subBank']
                loan_reason = request.form['loanReason']
                loan_amount = request.form['loanAmount']
                loanNumber = request.form['loanNumber']
                received_date = request.form['receivedDate']
                roi = request.form['interest']
                screening_date = request.form['screeningDate']
                jr_letter_date = request.form['jrLetterDate']
                jr_letter_number = request.form['jrLetterNumber']
                no_of_demands = request.form['noOfDemands']
                status = request.form['status']
                status_date = request.form['statusDate']
                ann_loan_id = request.form['annualLoanID']
                no_of_shgs = request.form['shgCount']
                user_id = user._id
                user_name = user.username
                pso_date = request.form['psoDate']
                ro_date = request.form['roDate']
                ro_number = request.form['roNumber']
                cheque_number = request.form['chequeNumber']
                cheque_date = request.form['chequeDate']
                ro_ref = request.form['roRef']

                account_head = "Loan To "+loan_category
                if status == "Covering Letter":
                    account = Account(invoice_date=status_date, nature_of_transaction="Debit",
                                      account_head=account_head, amount=loan_amount, loan_id=_id,
                                      user_id=user_id, user_name=user_name, depositing_bank=bank, ledger="Sub",
                                      cleared="No", cheque_date=status_date)
                    account.save_to_mongo()

                application = Database.find("loans", {"_id": _id})
                amount_to_pay = 0

                for result_object in application[0:1]:
                    amount_to_pay = result_object['amount_yet_to_pay']

                LoanApplication.update_loan_app(applicant_name=applicant_name, loan_category=loan_category, age=age,
                                                gender=gender, address=address, district=district,
                                                annual_income=annual_income,
                                                caste=caste, bank=bank, loan_reason=loan_reason, loan_amount=loan_amount,
                                                received_date=received_date, status=status, status_date=status_date,
                                                ann_loan_id=ann_loan_id, user_id=user_id, user_name=user_name,
                                                no_of_shgs=no_of_shgs, loan_id=_id, cheque_number=cheque_number,
                                                roi=roi, no_of_demands=no_of_demands, sub_bank=sub_bank,
                                                amount_to_pay=amount_to_pay, father_name=applicant_father_name,
                                                loan_number=loanNumber, screening_date=screening_date,
                                                jr_letter_number=jr_letter_number, jr_letter_date=jr_letter_date,
                                                ro_date=ro_date, pso_date=pso_date, amount_per_member=None,
                                                strength=None, shg_name=None, ro_number=ro_number,
                                                post_pso_ref=ro_ref, bank_district=bank_district, cheque_date=cheque_date)

                return render_template('application_added_update.html', user=user, application_id=_id)

            else:
                user = User.get_by_email(email)
                loan_category = request.form['loanCategory']
                district = request.form['district']
                bank_district = request.form['bankDistrict']
                bank = request.form['bankName']
                sub_bank = request.form['subBank']
                loan_reason = request.form['loanReason']
                loanNumber = request.form['loanNumber']
                loan_amount = request.form['loanAmount']
                received_date = request.form['receivedDate']
                screening_date = request.form['screeningDate']
                roi = request.form['interest']
                no_of_demands = request.form['noOfDemands']
                status = request.form['status']
                status_date = request.form['statusDate']
                jr_letter_date = request.form['jrLetterDate']
                jr_letter_number = request.form['jrLetterNumber']
                ann_loan_id = request.form['annualLoanID']
                no_of_shgs = int(request.form['shgCount'])
                inv_id = int(request.form['invIDCTR'])
                user_id = user._id
                user_name = user.username
                cheque_number = request.form['chequeNumber']
                cheque_date = request.form['chequeDate']
                ro_date = request.form['roDate']
                ro_number = request.form['roNumber']

                deletion_variable = True

                for i in range(int(inv_id)+1):
                    print(inv_id)
                    shg_name_string = "sn" + str(i)
                    amount_per_member_string = "apm" + str(i)
                    strength_string = "strength" + str(i)
                    ta = "ta" + str(i)
                    sb = "sb" + str(i)
                    lid = "lid" + str(i)

                    shg_name = request.form[shg_name_string]
                    amount_per_member = request.form[amount_per_member_string]
                    strength = request.form[strength_string]
                    sub_bank = request.form[sb]

                    if deletion_variable:
                        deletion = request.form['delID']
                        deletion_array = deletion.split("|")

                        for deletion in deletion_array:
                            LoanApplication.deletefrom_mongo(_id=deletion)
                        deletion_variable = False

                    if request.form[lid] != "":
                        _id = request.form[lid]

                        LoanApplication.update_loan_app(applicant_name=None, loan_category=loan_category, age=None,
                                                        gender=None, address=None, district=district,
                                                        annual_income=None, caste=None, bank=bank, loan_reason=loan_reason,
                                                        loan_amount=loan_amount, received_date=received_date, status=status,
                                                        status_date=status_date, ann_loan_id=ann_loan_id, user_id=user_id,
                                                        user_name=user_name, no_of_shgs=no_of_shgs, loan_id=_id,
                                                        cheque_number=cheque_number, roi=roi, no_of_demands=no_of_demands,
                                                        sub_bank=sub_bank, amount_to_pay=amount_to_pay, father_name=None,
                                                        loan_number=loanNumber, screening_date=screening_date,
                                                        jr_letter_number=jr_letter_number,
                                                        jr_letter_date=jr_letter_date, ro_date=ro_date, pso_date=None,
                                                        amount_per_member=amount_per_member, strength=strength,
                                                        shg_name=shg_name, ro_number=ro_number, bank_district=bank_district,
                                                        post_pso_ref=None, cheque_date=cheque_date)
                    else:
                        application = LoanApplication(loan_category=loan_category, district=district, bank=bank,
                                                      loan_reason=loan_reason, loan_amount=loan_amount,
                                                      received_date=received_date, status=status, shg_name=shg_name,
                                                      amount_per_member=amount_per_member, strength=strength,
                                                      status_date=status_date, ann_loan_id=ann_loan_id,
                                                      user_id=user_id, user_name=user_name, cheque_number=cheque_number,
                                                      sub_bank=sub_bank, roi=roi, no_of_demands=no_of_demands,
                                                      screening_date=screening_date, loan_number=loanNumber,
                                                      jr_letter_date=jr_letter_date, jr_letter_number=jr_letter_number,
                                                      post_pso_ref_no=None, bank_district=bank_district, caste=None,
                                                      ro_date=ro_date, pso_date=None, cheque_date=cheque_date)

                        application.save_to_mongo()

                return render_template('application_added_update.html', application=application, user=user)

    else:
        return render_template('login_fail.html')


@app.route('/loanFinancial/<string:_id>', methods=['POST', 'GET'])
def loan_financial_form(_id):
    email = session['email']
    if email is not None:
        if request.method == 'GET':
            user = User.get_by_email(email)
            return render_template('addFinancial.html', user=user, application_id=_id)

        else:
            user = User.get_by_email(email)
            application = Database.find("loans", {"_id": _id})

            dem_count, roi = 0, 0
            ro_number, bank, district, loan_category, sub_bank = None, None, None, None, None

            for result_object in application[0:1]:
                dem_count = result_object['no_of_demands']
                roi = result_object['roi']
                loan_category = result_object['loan_category']
                sub_bank = result_object['sub_bank']
                bank = result_object['bank']
                district = result_object['district']
                ro_number = result_object['ro_number']

            var_date = []
            var_principal_demand = []
            var_interest_demand = []
            var_dem_number = []

            for i in range(int(dem_count)):
                var_form_date = "d"+str(i+1)
                var_form_principal_demand = "pd"+str(i+1)
                var_form_interest_demand = "id"+str(i+1)
                var_form_dem_number = "s"+str(i+1)

                var_date.append(request.form[var_form_date])
                var_principal_demand.append(request.form[var_form_principal_demand])
                var_interest_demand.append(request.form[var_form_interest_demand])
                var_dem_number.append(request.form[var_form_dem_number])

            loan_amount = request.form['loanAmount']
            sanction_date = request.form['receivedDate']
            user_id = user._id
            user_name = user.username
            loan_id = request.form['loanID']

            for i in range(int(dem_count)):
                demand_object = Demand(loan_category=loan_category, district_bank=bank, sub_bank=sub_bank,
                                       district=district, loan_amount=loan_amount, demand_number=var_dem_number[i],
                                       demand_date=var_date[i], principal_demand=var_principal_demand[i],
                                       interest_demand=var_interest_demand[i], loan_id=_id, user_id=user_id,
                                       user_name=user_name, ann_id=loan_id, loan_sanction_date=sanction_date,
                                       roi=roi, no_of_demands=dem_count, ro_number=ro_number)

                demand_object.save_to_mongo()

        return render_template('added.html',  user=user)

    else:
        return render_template('login_fail.html')


@app.route('/updateDemand/<string:_id>', methods=['POST', 'GET'])
def update_loan_financial_form(_id):
    email = session['email']
    if email is not None:
        if request.method == 'GET':
            user = User.get_by_email(email)

            demandm1 = None
            demand = Database.find("Demands", {"_id": _id})
            lsd, demand_date, chequem1_date = None, None, None
            loan_amount = 0
            roi, principal_demand, interest_demand, interest_due, principal_due, demand_number = 0, 0, 0, 0, 0, 0

            for result_object in demand[0:1]:
                lsd = result_object['loan_sanction_date']
                demand_date = result_object['demand_date']
                demand_number = int(result_object['demand_number'])
                roi = int(result_object['roi'])
                principal_demand = int(result_object['principal_demand'])
                loan_amount = int(result_object['loan_amount'])

            if demand_number == 1:
                days = (demand_date-lsd).days
                interest_demand = (days*loan_amount*roi)/(365*100)
            else:
                demand_numberm1 = demand_number-1
                demandm1 = Database.find("Demands", {"demand_number": str(demand_numberm1)})
                for result_object in demandm1[0:1]:
                    principal_due = result_object['closing_balance_principal_due']
                    principal_for_interest = result_object['closing_balance_principal_ndue']
                    interest_due = result_object['closing_balance_interest_due']
                    demandm1_date = result_object['demand_date']
                    days = (demand_date-demandm1_date).days
                    interest_demand = (days*principal_for_interest*roi)/(365*100)

            principal_demand += principal_due
            interest_demand += interest_due

            return render_template('updateFinancial.html', user=user, demand_id=_id,
                                   total_principal_demand=principal_demand, total_interest_demand=interest_demand)

        else:
            user = User.get_by_email(email)
            demand_number = request.form['demandNumber']
            demand_date = request.form['demandDate']
            cheque_number = request.form['chequeNumber']
            cheque_date = request.form['chequeDate']
            principal_demand = int(request.form['demandPrincipalPayable'])
            interest_demand = int(request.form['demandInterestPayable'])
            chequeAmount = int(request.form['totalChequeAmount'])

            demand_date1 = (datetime.combine(datetime.strptime(demand_date, '%Y-%m-%d').date(),
                                             datetime.now().time()))
            cheque_date1 = (datetime.combine(datetime.strptime(cheque_date, '%Y-%m-%d').date(),
                                             datetime.now().time()))

            demand = Database.find("Demands", {"_id": _id})

            loan_amount, roi, penal_interest, belated_interest, opening_balance_principal_ndue = 0, 0, 0, 0, 0
            original_principal_demand, original_interest_demand = 0, 0
            sub_bank, chequem1_date, loan_id = None, None, None

            for result_object in demand[0:1]:
                loan_amount = int(result_object['loan_amount'])
                roi = int(result_object['roi'])
                original_principal_demand = int(result_object['principal_demand'])
                loan_id = result_object['loan_id']

            if int(demand_number) == 1:
                days_delayed = (cheque_date1 - demand_date1).days
                opening_balance_principal_ndue = loan_amount
                total_paid = principal_demand       #+interest_collected
                if days_delayed > 0:
                    penal_interest = (days_delayed*total_paid*5)/(365*100)
                    belated_interest = (days_delayed*total_paid*roi)/(365 * 100)
                else:
                    penal_interest = 0
                    belated_interest = 0

            else:
                demand_numberm1 = int(demand_number)-1

                demandm1 = Database.find("Demands", {"$and": [{"demand_number": str(demand_numberm1)},
                                                              {"loan_id": loan_id}]})

                for result_object in demandm1[0:1]:
                    opening_balance_principal_ndue = int(result_object['closing_balance_principal_ndue'])
                    original_principal_demand = int(result_object['principal_demand'])
                    original_interest_demand = int(result_object['interest_demand'])
                    chequem1_date = result_object['cheque_date']
                    sub_bank = result_object['sub_bank']

                days_delayed_old_due = (demand_date1-chequem1_date).days
                days_delayed = (cheque_date1 - demand_date1).days

                if days_delayed_old_due > 0:
                    total_old_due = (principal_demand-original_principal_demand)                #+(interest_demand-original_interest_demand)
                    penal_interest_old_due = (days_delayed_old_due*total_old_due*5)/(365*100)
                    belated_interest_old_due = (days_delayed_old_due*total_old_due*roi)/(365*100)
                else:
                    penal_interest_old_due = 0
                    belated_interest_old_due = 0

                if days_delayed > 0:
                    penal_interest_current_demand = (days_delayed*principal_demand*5)/(365*100)
                    belated_interest_current_demand = (days_delayed*principal_demand*roi)/(365*100)
                else:
                    penal_interest_current_demand = 0
                    belated_interest_current_demand = 0

                penal_interest = penal_interest_old_due+penal_interest_current_demand
                belated_interest = belated_interest_old_due+belated_interest_current_demand

            if (chequeAmount - (penal_interest+belated_interest)) >= interest_demand:
                interest_collected = interest_demand
            else:
                interest_collected = chequeAmount - (penal_interest+belated_interest)
            closing_balance_interest_due = interest_demand-interest_collected

            if (chequeAmount - (penal_interest+belated_interest+interest_collected)) > 0:
                principal_collected = chequeAmount - (penal_interest+belated_interest+interest_collected)
            else:
                principal_collected = 0

            principal_collected1 = principal_collected - (penal_interest+belated_interest)
            closing_balance_principal_due = principal_demand-principal_collected1
            closing_balance_principal_ndue = opening_balance_principal_ndue-original_principal_demand
            service_charge = (3/roi)*interest_collected

            demand = Database.find("loans", {"_id": loan_id})
            pending_amount = 0
            loan_category, dem_count = None, None

            for result_object in demand[0:1]:
                pending_amount = int(result_object['amount_yet_to_pay'])
                loan_category = result_object['loan_category']
                dem_count = result_object['no_of_demands']

            amount_yet_to_pay_loan = (closing_balance_interest_due+closing_balance_principal_due+penal_interest+belated_interest)-(principal_collected1+interest_collected)
            update_amount = pending_amount+amount_yet_to_pay_loan

            Demand.update_demand(demand_id=_id, demand_number=demand_number, demand_date=demand_date1,
                                 cheque_number=cheque_number, cheque_date=cheque_date1,
                                 principal_collected=principal_collected1, interest_collected=interest_collected,
                                 closing_balance_interest_due=closing_balance_interest_due,
                                 closing_balance_principal_due=closing_balance_principal_due,
                                 closing_balance_principal_ndue=closing_balance_principal_ndue,
                                 penal_interest=penal_interest, belated_interest=belated_interest,
                                 service_charge=service_charge, no_of_demands=dem_count)

            LoanApplication.update_pend_amount(amount_yet_to_be_paid=int(update_amount), loan_id=loan_id)

            account = Account(invoice_date=cheque_date1.strftime('%Y-%m-%d'), nature_of_transaction="Credit",
                              amount=loan_amount, loan_id=loan_id, user_id=user._id, user_name=user.username,
                              depositing_bank=sub_bank, adjustment_voucher="No", ledger="Sub",
                              interest=belated_interest+interest_collected, penal_interest=penal_interest,
                              service_charge=service_charge, principal=principal_collected,
                              cheque_date=cheque_date)
            account.save_to_mongo()

            return render_template('application_added.html', user=user)

    else:
        return render_template('login_fail.html')


@app.route('/ViewDemandsByLoan/<string:loan_id>')
def all_demands_view(loan_id):
    email = session['email']
    user = User.get_by_email(email)

    if email is not None:
        return render_template('ViewDemands.html', user=user, loan_id=loan_id)
    else:
        return render_template('login_fail.html', user=user)


@app.route('/rawDemandsByLoan/<string:loan_id>')
def raw_demands_by_loan_id(loan_id):
    loan = []
    loan_dict = Database.find("Demands", {"loan_id": loan_id})

    for tran in loan_dict:
        loan.append(tran)

    single_loan = json.dumps(loan, default=json_util.default)

    return single_loan


@app.route('/raw_receipt/<string:_id>')
def get_raw_receipt(_id):
    all_credit = []
    all_credit_dict = Database.find("accounts", {'_id': _id})
    for tran in all_credit_dict:
        all_credit.append(tran)

    all_credits = json.dumps(all_credit, default=json_util.default)

    return all_credits


@app.route('/delete_application/<string:_id>')
def delete_application(_id):
    email = session['email']
    user = User.get_by_email(email)

    LoanApplication.deletefrom_mongo(_id=_id)

    return render_template('deleted.html', user=user)


@app.route('/Credit')
def get_credits():
    all_credit = []
    all_credit_dict = Database.find("accounts", {'nature_of_transaction': "Credit"})
    for tran in all_credit_dict:
        all_credit.append(tran)

    all_credits = json.dumps(all_credit, default=json_util.default)

    return all_credits


@app.route('/Debit')
def get_debits():
    all_debit = []
    all_debit_dict = Database.find("accounts", {'nature_of_transaction': "Debit"})
    for tran in all_debit_dict:
        all_debit.append(tran)

    all_debits = json.dumps(all_debit, default=json_util.default)

    return all_debits


@app.route('/RawLoanApplication')
def raw_all_applications():
    all_loans = []
    all_loans_dict = Database.find("loans", {})
    for tran in all_loans_dict:
        all_loans.append(tran)

    all_loan = json.dumps(all_loans, default=json_util.default)

    return all_loan


@app.route('/RawLoans/<string:status>')
def raw_applications(status):
    all_loans = []
    all_loans_dict = Database.find("loans", {"status": status})
    for tran in all_loans_dict:
        all_loans.append(tran)

    all_loan = json.dumps(all_loans, default=json_util.default)

    return all_loan


@app.route('/demand/<string:_id>')
def get_demand_by_id(_id):
    loan = []
    loan_dict = Database.find("Demands", {"_id": _id})
    for tran in loan_dict:
        loan.append(tran)

    single_loan = json.dumps(loan, default=json_util.default)

    return single_loan


@app.route('/loan/<string:_id>')
def get_application_by_id(_id):
    loan = []
    loan_dict = Database.find("loans", {"_id": _id})
    for tran in loan_dict:
        loan.append(tran)

    single_loan = json.dumps(loan, default=json_util.default)

    return single_loan


@app.route('/getLoansByIdentfierLoans/<string:ann_loan_id>')
def get_applications_by_identifier(ann_loan_id):
    loan = []

    loan_dict = Database.find("loans", {"ann_loan_id": ann_loan_id})

    for tran in loan_dict:
        loan.append(tran)

    single_loan = json.dumps(loan, default=json_util.default)

    return single_loan


@app.route('/getLoansByIdentfier/<string:ann_loan_id>')
def get_application_by_identifier(ann_loan_id):
    loan = []

    loan_dict = Database.find("Demands", {"loan_id": ann_loan_id})

    for tran in loan_dict:
        loan.append(tran)

    single_loan = json.dumps(loan, default=json_util.default)

    return single_loan


@app.route('/rawLoanFinancial/<string:_id>')
def get_application_financial_by_id(_id):
    loan = []
    loan_dict = Database.find("loanFinancial", {"loan_id": _id})
    for tran in loan_dict:
        loan.append(tran)

    single_loan = json.dumps(loan, default=json_util.default)

    return single_loan


@app.route('/Debit_View')
def debit_view():
    email = session['email']
    user = User.get_by_email(email)

    if email is not None:
        return render_template('DebitView.html', user=user)
    else:
        return render_template('login_fail.html', user=user)


@app.route('/Credit_View')
def credit_view():
    email = session['email']
    user = User.get_by_email(email)

    if email is not None:
        return render_template('CreditView.html', user=user)
    else:
        return render_template('login_fail.html', user=user)


@app.route('/ViewAllLoanApplications')
def all_loans_view():
    email = session['email']
    user = User.get_by_email(email)

    if email is not None:
        return render_template('ViewLoans.html', user=user)
    else:
        return render_template('login_fail.html', user=user)


@app.route('/loans/<string:status>')
def loans_view(status):
    email = session['email']
    user = User.get_by_email(email)

    stat = status.replace("_", " ")

    if email is not None:
        return render_template('ViewLoansByCategory.html', user=user, stat=stat)
    else:
        return render_template('login_fail.html', user=user)


@app.route('/ReviewLoanApplication/<string:_id>')
def status_review(_id):
    email = session['email']
    user = User.get_by_email(email)

    demandm1 = Database.find("loans", {"_id": _id})
    annual_loan_id = None

    for result_object in demandm1[0:1]:
        annual_loan_id = result_object['ann_loan_id']

    if email is not None:
        return render_template('Application_Review.html', user=user, application_id=_id, annual_loan_id=annual_loan_id)
    else:
        return render_template('login_fail.html', user=user)


@app.route('/trail_balance', methods=['POST', 'GET'])
def trail_balance():
    email = session['email']
    user = User.get_by_email(email)

    if email is not None:
        if request.method == 'GET':
            return render_template('BetweenDates.html', user=user)

        else:
            start_date = request.form['startDate']
            end_date = request.form['endDate']
            return render_template('TrailBalanceSheet.html', user=user, start_date=start_date, end_date=end_date)

    else:
        return render_template('login_fail.html', user=user)


@app.route('/accounting_statements', methods=['POST', 'GET'])
def account_statements():
    email = session['email']
    user = User.get_by_email(email)

    if email is not None:
        if request.method == 'GET':
            return render_template('BetweenDatesAccount.html', user=user)

        else:
            start_date = request.form['startDate']
            end_date = request.form['endDate']

            return render_template('account_statements.html', user=user, start_date=start_date,
                                   end_date=end_date)

    else:
        return render_template('login_fail.html', user=user)


@app.route('/bank_accounting_statements', methods=['POST', 'GET'])
def bank_account_statements():
    email = session['email']
    user = User.get_by_email(email)

    if email is not None:
        if request.method == 'GET':
            return render_template('BetweenDatesBank.html', user=user)

        else:
            start_date = request.form['startDate']
            end_date = request.form['endDate']
            bank = request.form['bank']
            interest = request.form['interestOnAccount']
            bank_charges = request.form['bankCharges']

            return render_template('bank_account_statements.html', user=user, start_date=start_date,
                                   end_date=end_date, bank=bank, interest=interest, bank_charges=bank_charges)

    else:
        return render_template('login_fail.html', user=user)


@app.route('/utilisation_certificate', methods=['POST', 'GET'])
def util_certificate():
    email = session['email']
    user = User.get_by_email(email)

    if email is not None:
        if request.method == 'GET':
            return render_template('BetweenDatesCategory.html', user=user)

        else:
            start_date = request.form['startDate']
            end_date = request.form['endDate']
            loan_category = request.form['loanCategory']

            return render_template('UtilisationCertificate.html', user=user, start_date=start_date,
                                   end_date=end_date, loan_category=loan_category)

    else:
        return render_template('login_fail.html', user=user)


@app.route('/get_pending_loans', methods=['POST', 'GET'])
def loanfinancial_getpost():
    email = session['email']
    user = User.get_by_email(email)

    if email is not None:
        if request.method == 'GET':
            return render_template('BetweenDatesCategoryDistrict.html', user=user)

        else:
            start_date = request.form['startDate']
            end_date = request.form['endDate']
            loan_category = request.form['loanCategory']
            bank = request.form['bank']

            return render_template('loanFinancialView.html', user=user, start_date=start_date,
                                   end_date=end_date, loan_category=loan_category, bank=bank)

    else:
        return render_template('login_fail.html', user=user)


@app.route('/otherAccountingStatements')
def otherAccountingStatements():
    email = session['email']
    user = User.get_by_email(email)

    if email is not None:
        return render_template('BetweenDatesOtherAccounts.html', user=user)

    else:
        return render_template('login_fail.html', user=user)


@app.route('/RawDemandsBetween/<string:bank>/<string:category>')
def raw_loan_financial_district_category(bank, category):
    all_transactions = []
    all_trans_dict = Database.find("loans", {"$and": [{"bank": bank},
                                                      {"loan_category": category},
                                                      {"$where": "this.amount_yet_to_pay > 0"}]})

    for tran in all_trans_dict:
        all_transactions.append(tran)

    all_t = json.dumps(all_transactions, default=json_util.default)

    return all_t


@app.route('/RawTrailBalance/<string:start_date>/<string:end_date>')
def raw_trail_balance(start_date, end_date):
    all_transactions = []

    start = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(),
                             datetime.now().time())
    end = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(),
                           datetime.now().time())
    all_trans_dict = Database.find("accounts", {"invoice_date": {"$gte": start, "$lt": end}})

    for tran in all_trans_dict:
        all_transactions.append(tran)

    all_t = json.dumps(all_transactions, default=json_util.default)

    return all_t


@app.route('/RawUC/<string:category>/<string:start_date>/<string:end_date>')
def raw_UC(category, start_date, end_date):
    category_applications = []

    start = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(),
                             datetime.now().time())
    end = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(),
                           datetime.now().time())
    category_applications_dict = Database.find("loans", {"$and": [{"loan_category": category},
                                                                  {"received_date": {"$gte": start, "$lt": end}}]})

    for tran in category_applications_dict:
        category_applications.append(tran)

    applications = json.dumps(category_applications, default=json_util.default)

    return applications


@app.route('/accounts_between_bank/<string:start_date>/<string:end_date>/<string:bank>')
def accounts_between_bank(start_date, end_date, bank):
    accounts = []

    start = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(),
                             datetime.now().time())
    end = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(),
                           datetime.now().time())
    accounts_dict = Database.find("accounts", {"$and": [{"invoice_date": {"$gte": start, "$lt": end}},
                                                        {"bank_account": bank}]})

    for tran in accounts_dict:
        accounts.append(tran)

    accounts_final = json.dumps(accounts, default=json_util.default)

    return accounts_final


@app.route('/accounts_between_HOA/<string:start_date>/<string:end_date>/<string:HOA>')
def accounts_between_hoa(start_date, end_date, HOA):
    accounts = []

    start = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(),
                             datetime.now().time())
    end = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(),
                           datetime.now().time())
    accounts_dict = Database.find("accounts", {"$and": [{"invoice_date": {"$gte": start, "$lt": end}},
                                                        {"account_head": HOA}]})

    for tran in accounts_dict:
        accounts.append(tran)

    accounts_final = json.dumps(accounts, default=json_util.default)

    return accounts_final


@app.route('/accounts_between_adjustmentVoucher/<string:start_date>/<string:end_date>/<string:YON>')
def accounts_between_adjvou(start_date, end_date, YON):
    accounts = []

    start = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(),
                             datetime.now().time())
    end = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(),
                           datetime.now().time())
    accounts_dict = Database.find("accounts", {"$and": [{"invoice_date": {"$gte": start, "$lt": end}},
                                                        {"adjustment_voucher": YON}]})

    for tran in accounts_dict:
        accounts.append(tran)

    accounts_final = json.dumps(accounts, default=json_util.default)

    return accounts_final


@app.route('/accounts_between_transaction/<string:start_date>/<string:end_date>/<string:trans>')
def accounts_between_debcred(start_date, end_date, trans):
    accounts = []

    start = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(),
                             datetime.now().time())
    end = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(),
                           datetime.now().time())
    accounts_dict = Database.find("accounts", {"$and": [{"invoice_date": {"$gte": start, "$lt": end}},
                                                        {"nature_of_transaction": trans}]})

    for tran in accounts_dict:
        accounts.append(tran)

    accounts_final = json.dumps(accounts, default=json_util.default)

    return accounts_final


@app.route('/accounts_between_ledger/<string:start_date>/<string:end_date>/<string:YON>')
def accounts_between_ledger(start_date, end_date, YON):
    accounts = []

    start = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(),
                             datetime.now().time())
    end = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(),
                           datetime.now().time())
    accounts_dict = Database.find("accounts", {"$and": [{"invoice_date": {"$gte": start, "$lt": end}},
                                                        {"ledger": YON}]})

    for tran in accounts_dict:
        accounts.append(tran)

    accounts_final = json.dumps(accounts, default=json_util.default)

    return accounts_final


@app.route('/accounts_between_ledger_accHead/<string:start_date>/<string:end_date>/<string:YON>/<string:HOA>')
def accounts_between_ledger_head(start_date, end_date, YON, HOA):
    accounts = []

    start = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(),
                             datetime.now().time())
    end = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(),
                           datetime.now().time())
    accounts_dict = Database.find("accounts", {"$and": [{"invoice_date": {"$gte": start, "$lt": end}},
                                                        {"account_head": HOA},
                                                        {"ledger": YON}]})

    for tran in accounts_dict:
        accounts.append(tran)

    accounts_final = json.dumps(accounts, default=json_util.default)

    return accounts_final


@app.route('/accounts_between_cds/<string:start_date>/<string:end_date>/<string:CDS>')
def accounts_between_cds(start_date, end_date, CDS):
    accounts = []

    start = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(),
                             datetime.now().time())
    end = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(),
                           datetime.now().time())

    accounts_dict = Database.find("accounts", {"$and": [{"invoice_date": {"$gte": start, "$lt": end}},
                                                        {"nature_of_transaction": CDS}]})

    for tran in accounts_dict:
        accounts.append(tran)

    accounts_final = json.dumps(accounts, default=json_util.default)

    return accounts_final


@app.route('/accounts_between/<string:start_date>/<string:end_date>')
def accounts_between(start_date, end_date):
    accounts = []

    start = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(),
                             datetime.now().time())
    end = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(),
                           datetime.now().time())
    accounts_dict = Database.find("accounts", {"$and": [{"invoice_date": {"$gte": start, "$lt": end}}]})

    for tran in accounts_dict:
        accounts.append(tran)

    accounts_final = json.dumps(accounts, default=json_util.default)

    return accounts_final


# @app.before_request
# def limit_remote_addr():
#     if request.headers.getlist("X-Forwarded-For")[0] == '106.208.39.7':
#         return abort(403)  # Forbidden

if __name__ == '__main__':
    app.run(port=4025, debug=True)
