from datetime import datetime

import pymongo
from bson import json_util
from flask import Flask, render_template, request, session, json, abort
from src.common.database import Database
from src.models.accounts import Account
from src.models.loan_financials import Demand
from src.models.loanapplication import LoanApplication
from src.models.user import User
from src.models.mini_demands import MiniDemand

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
                                "PRINTING AND STATIONERY": "Other Expenses",
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
                              ledger=ledger, cleared="No", cheque_date=cheque_date, narration=narration,
                              clearing_credit_balance=0, clearing_debit_balance=0)

            account.save_to_mongo()

            return render_template('receipt_added.html', account=account, user=user)

    else:
        return render_template('login_fail.html')


@app.route('/new_multi_receipt/<string:user_id>', methods=['POST', 'GET'])
def multi_receipt_form(user_id):
    email = session['email']
    if email is not None:
        if request.method == 'GET':
            user = User.get_by_id(user_id)
            return render_template('multi_receipt_form.html', user=user)

        else:
            user = User.get_by_id(user_id)
            invoice_date = request.form['invoiceDate']
            voucher_date = request.form['voucherDate']
            mode = request.form['mode']
            adjustmentVoucher = request.form['adjustmentVoucher']
            ledger = request.form['ledger']
            nature_of_transaction = request.form['natureOfTransaction']
            bank_account = request.form['bankAccount']
            narration = request.form['narration']
            cheque_num = request.form['cheque']
            pvoucher = request.form['paymentVoucher']
            depoBank = request.form['depositingBank']
            cheque_date = request.form['chequeDate']
            inv_id = request.form['invID']
            user_id = user_id
            user_name = user.username

            account, account_head, clearing_balance_debit, clearing_balance_credit = None, None, None, None
            new_debit_balance, new_credit_balance = 0, 0
            cl_credit_old, cl_debit_old = 0, 0
            application = None

            for i in range(int(inv_id)):
                s_no = "sno" + str(i)
                acchead = "acchead" + str(i)
                cl_debit_balance = "debit_amount" + str(i)
                cl_credit_balance = "credit_amount" + str(i)

                serial_no = request.form[s_no]
                account_head = request.form[acchead]
                clearing_balance_debit = request.form[cl_debit_balance]
                clearing_balance_credit = request.form[cl_credit_balance]

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
                                    "PRINTING AND STATIONERY": "Other Expenses",
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

                application = Database.find("trailBalance", {"Head of Accounts": account_head})

                account = Account(invoice_date=invoice_date, nature_of_transaction=nature_of_transaction,
                                  account_head=account_head, bank_account=bank_account,
                                  user_id=user_id, user_name=user_name, doc_account_head=doc_account_head,
                                  cheque_number=cheque_num, payment_voucher=pvoucher, depositing_bank=depoBank,
                                  voucher_date=voucher_date, adjustment_voucher=adjustmentVoucher,
                                  ledger=ledger, cleared="No", cheque_date=cheque_date, narration=narration,
                                  clearing_credit_balance=clearing_balance_credit, mode=mode,
                                  clearing_debit_balance=clearing_balance_debit, amount=0)

                for result_object in application:
                    cl_credit_old = int(result_object['Cl']['Credit Bal'])
                    cl_debit_old = int(result_object['Cl']['Debit Bal'])

                    if int(clearing_balance_debit) >= 0 & int(cl_debit_old) >= 0 & int(clearing_balance_credit) == 0:
                        new_debit_balance = int(clearing_balance_debit) + int(cl_debit_old)
                        new_credit_balance = int(cl_credit_old)
                    elif int(clearing_balance_credit) >= 0 & int(cl_credit_old) >= 0 & int(clearing_balance_debit) == 0:
                        new_credit_balance = int(clearing_balance_credit) + int(cl_credit_old)
                        new_debit_balance = int(cl_debit_old)
                    elif int(clearing_balance_credit) >= 0 & int(cl_debit_old) >= 0 & int(clearing_balance_debit) == 0:
                        if int(clearing_balance_credit) <= int(cl_debit_old):
                            new_debit_balance = cl_debit_old - int(clearing_balance_credit)
                            new_credit_balance = int(cl_credit_old)
                        else:
                            new_debit_balance = 0
                            new_credit_balance = int(clearing_balance_credit) - int(cl_debit_old)
                    elif int(clearing_balance_debit) >= 0 & int(cl_credit_old) >= 0 & int(clearing_balance_credit) == 0:
                        if int(clearing_balance_debit) <= int(cl_credit_old):
                            new_credit_balance = int(cl_credit_old) - int(clearing_balance_debit)
                            new_debit_balance = int(cl_debit_old)
                        else:
                            new_credit_balance = 0
                            new_debit_balance = int(clearing_balance_debit) - int(cl_credit_old)
                    print(cl_credit_old, cl_debit_old, clearing_balance_credit, clearing_balance_debit,
                          new_debit_balance, new_credit_balance)

                    # Account.update_ledger_balance(head_of_accounts=account_head,
                    #                               credit_balance=new_credit_balance,
                    #                               debit_balance=new_debit_balance)

                    account.save_to_mongo()

            return render_template('receipt_added_multi.html', account=account, user=user, ncb=new_credit_balance,
                                   ndb=new_debit_balance, cl_d_bal=clearing_balance_debit,
                                   cl_c_bal=clearing_balance_credit, deb_old=cl_debit_old, cre_old=cl_credit_old,
                                   application=application)

    else:
        return render_template('login_fail.html')


@app.route('/update_Receipt/<string:_id>', methods=['POST', 'GET'])
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
            cl_debit_amount = request.form['total_debit']
            cl_credit_amount = request.form['total_credit']
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
                                "PRINTING AND STATIONERY": "Other Expenses",
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
                                   account_head=account_head, bank_account=bank_account,
                                   user_id=user_id, user_name=user_name, doc_account_head=doc_account_head, _id=_id,
                                   payment_voucher=pvoucher, cheque_number=cheque_num, depositing_bank=depoBank,
                                   adjustment_voucher=adjustmentVoucher, voucher_date=voucher_date, ledger=ledger,
                                   cleared=cleared, cheque_date=cheque_date, narration=narration,
                                   clearing_credit_balance=cl_credit_amount, clearing_debit_balance=cl_debit_amount,
                                   amount=amount)

            application = Database.find("accounthead", {"Head of Accounts": account_head})

            cl_credit_old, cl_debit_old = 0, 0

            for result_object in application[0:1]:
                cl_credit_old = int(result_object['Cl']['Credit Bal'])
                cl_debit_old = int(result_object['Cl']['Debit Bal'])

            application = Database.find("accounts", {"_id": _id})

            new_credit, new_debit = 0, 0

            for result_object in application[0:1]:
                new_credit = int(cl_credit_amount) - int(result_object['clearing_credit_balance'])
                new_debit = int(cl_debit_amount) - int(result_object['clearing_debit_balance'])

            print(cl_credit_amount, cl_debit_amount, cl_credit_old, cl_debit_old)

            Account.update_ledger_balance(head_of_accounts=account_head,
                                          credit_balance=new_credit + cl_credit_old,
                                          debit_balance=new_debit+ cl_debit_old)

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
                annual_loan_id = None

                for result_object in application[0:1]:
                    amount_to_pay = result_object['amount_yet_to_pay']
                    annual_loan_id = result_object['ann_loan_id']

                LoanApplication.update_loan_app(applicant_name=applicant_name, loan_category=loan_category, age=age,
                                                gender=gender, address=address, district=district,
                                                annual_income=annual_income,
                                                caste=caste, bank=bank, loan_reason=loan_reason,
                                                loan_amount=loan_amount,
                                                received_date=received_date, status=status, status_date=status_date,
                                                ann_loan_id=ann_loan_id, user_id=user_id, user_name=user_name,
                                                no_of_shgs=no_of_shgs, loan_id=_id, cheque_number=cheque_number,
                                                roi=roi, no_of_demands=no_of_demands, sub_bank=sub_bank,
                                                amount_to_pay=amount_to_pay, father_name=applicant_father_name,
                                                loan_number=loanNumber, screening_date=screening_date,
                                                jr_letter_number=jr_letter_number, jr_letter_date=jr_letter_date,
                                                ro_date=ro_date, pso_date=pso_date, amount_per_member=None,
                                                strength=None, shg_name=None, ro_number=ro_number,
                                                post_pso_ref=ro_ref, bank_district=bank_district,
                                                cheque_date=cheque_date)

                application_also_update = Database.find("loans", {"ann_loan_id": annual_loan_id})

                for result_object in application_also_update:
                    identifier_similar_id = result_object['_id']
                    received_date = result_object['received_date']

                    LoanApplication.update_loan_app_similar(loan_id=identifier_similar_id, sub_bank=sub_bank,
                                                            screening_date=screening_date,
                                                            jr_letter_number=jr_letter_number,
                                                            jr_letter_date=jr_letter_date,
                                                            ro_date=ro_date, pso_date=pso_date, ro_number=ro_number,
                                                            post_pso_ref=ro_ref, bank_district=bank_district,
                                                            cheque_date=cheque_date, received_date=received_date)

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


@app.route('/loanFinancial/<string:_id>/<string:ro_number>/<string:loan_amount>', methods=['POST', 'GET'])
def loan_financial_form(_id, ro_number, loan_amount):
    email = session['email']
    if email is not None:
        if request.method == 'GET':
            user = User.get_by_email(email)
            return render_template('addFinancial.html', user=user, application_id=_id, ro_number=ro_number,
                                   loan_amount=loan_amount)

        else:
            user = User.get_by_email(email)
            application = Database.find("loans", {"ann_loan_id": _id,
                                                  "ro_number": ro_number})

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

            print(dem_count)

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

            demand_object = None

            for i in range(int(dem_count)):
                demand_object = Demand(loan_category=loan_category, district_bank=bank, sub_bank=sub_bank,
                                       district=district, loan_amount=loan_amount, demand_number=var_dem_number[i],
                                       demand_date=var_date[i], principal_demand=var_principal_demand[i],
                                       interest_demand=var_interest_demand[i], loan_id=_id, user_id=user_id,
                                       user_name=user_name, ann_id=loan_id, loan_sanction_date=sanction_date,
                                       roi=roi, no_of_demands=dem_count, ro_number=ro_number)

                demand_object.save_to_mongo()

        return render_template('added.html',  user=user, demand=dem_count)

    else:
        return render_template('login_fail.html')


@app.route('/updateDemand/<string:_id>/<string:late_interest>/<string:belated_int>/<string:penal_int>/'
           '<string:p_due>/<string:p_ndue>/<string:i_due>',
           methods=['POST', 'GET'])
def update_loan_financial_form(_id, late_interest, belated_int, penal_int, p_due, p_ndue, i_due):
    email = session['email']
    if email is not None:
        if request.method == 'GET':
            user = User.get_by_email(email)

            demandm1 = None
            demand = Database.find("Demands", {"_id": _id})
            loan_id, lsd, demand_date, chequem1_date = None, None, None, None
            loan_amount = 0
            roi, principal_demand, interest_demand, interest_due, principal_due, demand_number, principal_for_interest = 0, 0, 0, 0, 0, 0, 0

            for result_object in demand[0:1]:
                lsd = result_object['loan_sanction_date']
                demand_date = result_object['demand_date']
                demand_number = int(result_object['demand_number'])
                roi = int(result_object['roi'])
                principal_demand = int(result_object['principal_demand'])
                interest_demand = int(result_object['interest_demand'])
                loan_amount = int(result_object['loan_amount'])
                loan_id = result_object['loan_id']

            if late_interest == 'NaN':
                late_interest = 0
                belated_int = 0
                penal_int = 0

            if demand_number == 1:
                total_interest_demand = interest_demand+int(late_interest)
            else:
                demand_numberm1 = demand_number-1
                demandm1 = Database.find("Demands", {"$and": [{"demand_number": str(demand_numberm1)},
                                                              {"loan_id": loan_id}]})

                for result_object in demandm1[0:1]:
                    principal_due = result_object['closing_balance_principal_due']
                    principal_for_interest = result_object['closing_balance_principal_ndue']
                    interest_due = result_object['closing_balance_interest_due']
                    demandm1_date = result_object['demand_date']
                    days = (demand_date-demandm1_date).days

                if principal_due is None:
                    principal_due = p_due
                    principal_for_interest = p_ndue
                    interest_due = i_due

                if penal_int == 'null':
                    penal_int = 0
                    belated_int = 0

                principal_demand += float(principal_due)
                total_interest_demand = float(interest_demand) + float(interest_due) + float(late_interest)

            return render_template('updateFinancial.html', user=user, demand_id=_id,
                                   total_principal_demand=principal_demand,
                                   total_interest_demand=total_interest_demand-(float(belated_int)+float(penal_int)),
                                   late_interest=late_interest, belated_int=belated_int, penal_int=penal_int, p_due=p_due,
                                   p_ndue=p_ndue, i_due=i_due)

        else:
            user = User.get_by_email(email)
            demand_number = request.form['demandNumber']
            demand_date = request.form['demandDate']
            demand_reference = request.form['demandReference']
            cheque_number = request.form['chequeNumber']
            cheque_date = request.form['chequeDate']
            cheque_date_issued = request.form['chequeDateIssued']
            principal_demand = int(request.form['demandPrincipalPayable'])
            interest_demand = int(request.form['demandInterestPayable'])
            penal = int(request.form['penalInterest'])
            belated = int(request.form['belatedInterest'])
            chequeAmount = int(request.form['totalChequeAmount'])
            cl_bal_p_due = int(request.form['principalDue'])
            principal_paid_collected = int(request.form['principalPaid'])
            interest_paid_collected = int(request.form['interestPaid'])
            cl_bal_i_due = int(request.form['interestDue'])
            cl_bal_p_ndue = int(request.form['overallDue'])
            service_sc = int(request.form['serviceCharge'])

            demand_date1 = (datetime.combine(datetime.strptime(demand_date, '%Y-%m-%d').date(),
                                             datetime.now().time()))
            cheque_date1 = (datetime.combine(datetime.strptime(cheque_date, '%Y-%m-%d').date(),
                                             datetime.now().time()))
            cheque_date_issued = (datetime.combine(datetime.strptime(cheque_date_issued, '%Y-%m-%d').date(),
                                                   datetime.now().time()))

            demand = Database.find("Demands", {"_id": _id})

            loan_amount, roi, penal_interest, belated_interest, opening_balance_principal_ndue = 0, 0, 0, 0, 0
            original_principal_demand, original_interest_demand = 0, 0
            sub_bank, previous_demand_cheque_date, loan_id = None, None, None
            opening_balance_principal_due, opening_balance_interest_due = 0, 0
            service_charge, total_old_due = 0, 0
            principal_collected, interest_collected = 0, 0
            late_interest, post_penal_belated_amount = 0, 0
            closing_balance_principal_due, closing_balance_interest_due, closing_balance_principal_ndue = 0, 0, 0

            for result_object in demand[0:1]:
                loan_amount = int(result_object['loan_amount'])
                roi = int(result_object['roi'])
                original_principal_demand = int(result_object['principal_demand'])
                original_interest_demand = int(result_object['interest_demand'])
                loan_id = result_object['loan_id']

            if int(demand_number) == 1:
                days_delayed = (cheque_date1 - demand_date1).days
                opening_balance_principal_ndue = loan_amount
                opening_balance_principal_due = original_principal_demand
                opening_balance_interest_due = original_interest_demand
                if days_delayed > 0:
                    penal_interest = penal
                    belated_interest = belated
                else:
                    penal_interest = 0
                    belated_interest = 0

                if chequeAmount > (penal+belated):
                    post_penal_belated_amount = float(chequeAmount) - (float(penal)+float(belated))
                    if post_penal_belated_amount > opening_balance_interest_due:
                        interest_collected = interest_demand
                        post_interest_late_fees_deduction = post_penal_belated_amount - interest_collected
                        service_charge = int(interest_collected) * 3 / roi
                        principal_collected = post_interest_late_fees_deduction + service_charge
                    else:
                        interest_collected = post_penal_belated_amount
                        principal_collected = 0
                        service_charge = int(interest_collected) * 3 / roi

            else:
                demand_numberm1 = int(demand_number)-1

                demandm1 = Database.find("Demands", {"$and": [{"demand_number": str(demand_numberm1)},
                                                              {"loan_id": loan_id}]})

                for result_object in demandm1[0:1]:
                    print(result_object)
                    opening_balance_principal_ndue = int(result_object['closing_balance_principal_ndue'])
                    opening_balance_principal_due = int(result_object['closing_balance_principal_due'])
                    opening_balance_interest_due = int(result_object['closing_balance_interest_due'])
                    total_old_due = opening_balance_principal_due + opening_balance_interest_due
                    previous_demand_cheque_date = result_object['cheque_date']
                    sub_bank = result_object['sub_bank']

                days_delayed_old_due = (demand_date1-previous_demand_cheque_date).days
                days_delayed_current_demand = (cheque_date1 - demand_date1).days

                if total_old_due > 0:
                    penal_interest_old_due = (days_delayed_old_due*total_old_due*5)/(365*100)
                    belated_interest_old_due = (days_delayed_old_due*total_old_due*roi)/(365*100)
                else:
                    penal_interest_old_due = 0
                    belated_interest_old_due = 0

                if days_delayed_current_demand > 0:
                    penal_interest_current_demand = (days_delayed_current_demand*principal_demand*5)/(365*100)
                    belated_interest_current_demand = (days_delayed_current_demand*principal_demand*roi)/(365*100)
                else:
                    penal_interest_current_demand = 0
                    belated_interest_current_demand = 0

                late_interest = float(belated_interest_old_due)+float(penal_interest_old_due)

                if chequeAmount > int(late_interest):
                    post_penal_belated_amount = float(chequeAmount) - late_interest
                    post_penal_belated_amount = float(post_penal_belated_amount) - (float(penal)+float(belated))
                    if post_penal_belated_amount > opening_balance_interest_due:
                        interest_collected = interest_demand
                        post_interest_late_fees_deduction = post_penal_belated_amount - interest_collected
                        service_charge = int(interest_collected) * 3 / roi
                        principal_collected = post_interest_late_fees_deduction + service_charge
                    else:
                        interest_collected = post_penal_belated_amount
                        service_charge = int(interest_collected) * 3 / roi
                        principal_collected = 0

            if float(belated_int) < 0:
                belated_int = 0
                penal_int = 0

            closing_balance_principal_ndue = opening_balance_principal_ndue - principal_collected
            closing_balance_interest_due = opening_balance_interest_due - interest_collected
            closing_balance_principal_due = opening_balance_principal_due - principal_collected

            demand = Database.find("loans", {"ann_loan_id": loan_id})
            pending_amount = 0
            loan_category, dem_count = None, None
            no_of_apps = demand.count()

            for result_object in demand[0:1]:
                pending_amount = int(result_object['amount_yet_to_pay'])
                dem_count = result_object['no_of_demands']

            amount_yet_to_pay_loan = (int(closing_balance_interest_due)+int(closing_balance_principal_due)+int(penal)+
                                      int(belated))-(int(principal_collected)+int(interest_collected))
            update_amount = int(pending_amount)+(int(amount_yet_to_pay_loan)/int(no_of_apps))

            Demand.update_demand(demand_id=_id, demand_number=demand_number, demand_date=demand_date,
                                 cheque_number=cheque_number, cheque_date=cheque_date,
                                 principal_collected=principal_paid_collected,
                                 interest_collected=interest_paid_collected,
                                 closing_balance_interest_due=cl_bal_i_due,
                                 closing_balance_principal_due=cl_bal_p_due,
                                 closing_balance_principal_ndue=cl_bal_p_ndue,
                                 penal_interest=penal, belated_interest=belated, cheque_amount=chequeAmount,
                                 service_charge=service_sc, no_of_demands=dem_count,
                                 demand_reference=demand_reference, cheque_date_issued=cheque_date_issued)

            LoanApplication.update_pend_amount(amount_yet_to_be_paid=int(update_amount), loan_id=loan_id)

            account = Account(invoice_date=cheque_date1.strftime('%Y-%m-%d'), nature_of_transaction="Credit",
                              amount=loan_amount, loan_id=loan_id, user_id=user._id, user_name=user.username,
                              depositing_bank=sub_bank, adjustment_voucher="No", ledger="Sub",
                              interest=float(belated_int)+float(interest_collected), penal_interest=penal_int,
                              service_charge=service_charge, principal=principal_collected,
                              cheque_date=cheque_date)
            account.save_to_mongo()

            return render_template('addedFinancialUpdate.html', user=user, closing=closing_balance_principal_due,
                                   closing_int=closing_balance_interest_due, principal=principal_collected,
                                   interest=interest_collected, penal=penal, belated=belated,
                                   post_penal_belated_amount=post_penal_belated_amount, late_interest=late_interest)

    else:
        return render_template('login_fail.html')


@app.route('/add_mini_demand/<string:_id>/<string:belated_int>/'
           '<string:penal_int>/<string:p_due>/<string:p_ndue>/<string:i_due>/'
           '<string:old_interest>/<string:demand_date>', methods=['POST', 'GET'])
def mini_demand_form(_id, belated_int, penal_int, p_due, p_ndue, i_due, old_interest, demand_date):
    email = session['email']
    if email is not None:
        if request.method == 'GET':
            user = User.get_by_email(email)

            previous_mini_demands = Database.find("mDemands", {"demand_id": _id})

            if previous_mini_demands.count() > 0:
                lmd = previous_mini_demands.count() - 1
                p_due = previous_mini_demands[lmd]['closing_balance_principal_due']
                p_ndue = previous_mini_demands[lmd]['closing_balance_principal_ndue']
                i_due = previous_mini_demands[lmd]['closing_balance_interest_due']

            # for demand in demands[0:1]:
            #     district = demand['district']
            #
            #
            return render_template('AddMiniDemand.html', user=user, demand_id=_id, belated_int=belated_int,
                                   penal_int=penal_int, p_due=p_due, p_ndue=p_ndue, i_due=i_due,
                                   old_interest=old_interest, demand_date=demand_date)

        else:
            user = User.get_by_email(email)
            demand_number = request.form['demandNumber']
            demand_reference = request.form['miniDemandReference']
            opening_balance_pdue = request.form['demandPrincipalPayable']
            opening_balance_idue = request.form['demandInterestPayable']
            cheque_date = request.form['chequeDate']
            cheque_date_issued = request.form['chequeIssueDate']
            penal_interest = request.form['penalInterest']
            belated_interest = request.form['belatedInterest']
            cheque_amount = request.form['totalChequeAmount']
            cheque_number = request.form['chequeNumber']
            principal_paid = request.form['principalPaid']
            interest_paid = request.form['interestPaid']
            service_charge = request.form['serviceCharge']
            closing_balance_pdue = request.form['principalDue']
            closing_balance_idue = request.form['interestDue']
            user_name = user.username

            cheque_date_issued = (datetime.combine(datetime.strptime(cheque_date_issued, '%Y-%m-%d').date(),
                                                   datetime.now().time()))

            district, district_bank, sub_bank, loan_category = None, None, None, None
            loan_id, previous_demand_number, demand_loan_id, loan_amount = None, None, None, None
            main_demand_closing_balance_principal_due, main_demand_closing_balance_interest_due = 0, 0
            main_demand_closing_balance_principal_ndue, main_demand_principal_collected = 0, 0
            main_demand_interest_collected, main_demand_penal_interest, main_demand_belated_interest = 0, 0, 0
            main_demand_service_charge, main_demand_cheque_amount = 0, 0
            mini_demand_principal_total, mini_demand_interest_total, closing_balance_not_due = 0, 0, 0
            opening_balance_principal_due, opening_balance_interest_due = 0, 0
            main_demand_principal_demand, main_demand_interest_demand = 0, 0
            main_demand_date, ann_id = None, None

            # Find the demand for which mini Demand is being added; Need to get auxiliary information
            demands = Database.find("Demands", {"_id": _id})

            # Auxiliary Information
            for demand in demands[0:1]:
                district = demand['district']
                district_bank = demand['district_bank']
                sub_bank = demand['sub_bank']
                main_demand_date = demand['demand_date']
                loan_category = demand['loan_category']
                loan_id = demand['loan_id']
                main_demand_principal_demand = int(demand['principal_demand'])
                main_demand_interest_demand = int(demand['interest_demand'])
                main_demand_principal_collected = int(demand['principal_collected'])
                main_demand_interest_collected = demand['interest_collected']
                main_demand_penal_interest = demand['penal_interest']
                main_demand_penal_interest = demand['belated_interest']
                main_demand_service_charge = demand['service_charge']
                loan_amount = demand['loan_amount']
                demand_loan_id = demand['loan_id']
                ann_id = demand['ann_id']
                previous_demand_number = int(demand['demand_number'])-1

            # Previous Main Demand to get Closing Balance; To calculate Principal Not Due

            if demand_number == 1:
                closing_balance_not_due = demands['closing_balance_principal_ndue']
                opening_balance_principal_due = demands['closing_balance_principal_due']
                opening_balance_interest_due = demands['closing_balance_interest_due']

            else:
                previous_demand = Database.find("Demands", {"$and": [{"demand_number": str(previous_demand_number)},
                                                                     {"loan_id": demand_loan_id}]})

                for prev_demand in previous_demand[0:1]:
                    closing_balance_not_due = prev_demand['closing_balance_principal_ndue']
                    opening_balance_principal_due = prev_demand['closing_balance_principal_due']
                    opening_balance_interest_due = prev_demand['closing_balance_interest_due']

            mini_dem = MiniDemand(user_name=user_name, cheque_number=cheque_number, cheque_date=cheque_date,
                                  principal_demand=opening_balance_pdue, demand_date=main_demand_date,
                                  interest_demand=opening_balance_idue, penal_interest=penal_interest,
                                  belated_interest=belated_interest, cheque_amount=cheque_amount,
                                  principal_collected=principal_paid, interest_collected=interest_paid,
                                  service_charge=service_charge, closing_balance_principal_due=closing_balance_pdue,
                                  closing_balance_interest_due=closing_balance_idue, demand_id=_id, district=district,
                                  district_bank=district_bank, sub_bank=sub_bank, loan_category=loan_category,
                                  loan_id=loan_id, demand_reference=demand_reference,
                                  m_demand_no=demand_number, loan_amount=loan_amount, ann_id=ann_id,
                                  cheque_date_issued=cheque_date_issued)

            mini_demands = Database.find("mDemands", {"demand_id": _id})

            # Cumulating principal & interest totals for final main_demand alterations;
            # [Closing Balance Principal & Interest Dues]
            for mdemand in mini_demands:
                main_demand_service_charge += int(mdemand['service_charge'])
                main_demand_cheque_amount += int(mdemand['cheque_amount'])
                mini_demand_principal_total += int(mdemand['principal_collected'])
                mini_demand_interest_total += int(float(mdemand['interest_collected']))

            main_demand_closing_balance_principal_ndue = \
                (int(closing_balance_not_due) - (main_demand_principal_collected + mini_demand_principal_total))
            main_demand_closing_balance_principal_due = \
                (int(opening_balance_principal_due) + int(main_demand_principal_demand)) - mini_demand_principal_total
            main_demand_closing_balance_interest_due = \
                (int(opening_balance_interest_due) + int(main_demand_interest_demand)) - mini_demand_interest_total

            Demand.update_main_demand(demand_id=_id,
                                      principal_collected=int(principal_paid)+int(main_demand_principal_collected),
                                      interest_collected=int(float(interest_paid)) +
                                                         int(float(main_demand_interest_collected)),
                                      penal_interest=int(main_demand_penal_interest)+int(penal_interest),
                                      belated_interest=int(main_demand_belated_interest) + int(belated_interest),
                                      service_charge=int(main_demand_service_charge)+int(service_charge),
                                      closing_balance_interest_due=main_demand_closing_balance_interest_due,
                                      closing_balance_principal_due=main_demand_closing_balance_principal_due,
                                      cheque_amount=int(cheque_amount)+int(main_demand_cheque_amount),
                                      closing_balance_principal_ndue=main_demand_closing_balance_principal_ndue)

            mini_dem.save_to_mongo()

            return render_template('mini_dem_added.html', mini_dem=mini_dem, user=user, district_bank=district_bank,
                                   b=sub_bank, closing_balance_pdue=closing_balance_pdue)

    else:
        return render_template('login_fail.html')


@app.route('/view_mini_demands/<string:_id>/<string:belated_int>/'
           '<string:penal_int>/<string:p_due>/<string:p_ndue>/<string:i_due>/'
           '<string:old_interest>', methods=['POST', 'GET'])
def view_mini_demand(_id, belated_int, penal_int, p_due, p_ndue, i_due, old_interest):
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        if belated_int == 'NaN':
            belated_int = 0
            penal_int = 0

        demand = Database.find("Demands", {"_id": _id})
        demand_date = None

        for result_object in demand[0:1]:
            demand_date = result_object['demand_date']

        return render_template('ViewMiniDemands.html', user=user, _id=_id, belated_int=belated_int,
                               penal_int=penal_int, p_due=p_due, p_ndue=p_ndue, i_due=i_due, demand_date=demand_date,
                               old_interest=old_interest)

    else:
        return render_template('login_fail.html')


@app.route('/ViewDemandsByLoan/<string:loan_id>/<string:ro_number>')
def loan_demands_view(loan_id, ro_number):
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        return render_template('ViewDemands.html', user=user, loan_id=loan_id, ro_number=ro_number)
    else:
        return render_template('login_fail.html', user=user)


@app.route('/ViewAccountHeadBalance')
def acc_head_balance_view():
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        return render_template('ViewAccountHead.html', user=user)
    else:
        return render_template('login_fail.html', user=user)


@app.route('/ledger_statement_download/<string:hoa>/<string:debit_bal>/<string:credit_bal>', methods=['POST', 'GET'])
def ledger_statement_view(hoa, debit_bal, credit_bal):
    email = session['email']
    user = User.get_by_email(email)
    if email is not None:
        if request.method == 'GET':
            return render_template('DownloadLedgerStatementWithinDates.html', user=user, hoa=hoa, debit_bal=debit_bal,
                                   credit_bal=credit_bal)
        else:
            start = request.form['startDate']
            end = request.form['endDate']
            user = User.get_by_email(email)

            return render_template('ledger_statement_download.html', end=end, start=start, hoa=hoa, user=user,
                                   debit_bal=debit_bal, credit_bal=credit_bal)

    else:
        return render_template('login_fail.html', user=user)


@app.route('/raw_ledger_statement_between/<string:hoa>/<string:start_date>/<string:end_date>')
def get_raw_footfall_entries_by_hoa_datefilter(hoa, start_date, end_date):
    district_destinations_array = []

    start = datetime.combine(datetime.strptime(start_date, '%Y-%m-%d').date(),
                             datetime.now().time())

    end = datetime.combine(datetime.strptime(end_date, '%Y-%m-%d').date(),
                           datetime.now().time())

    district_destinations = Database.find("accounts", {"$and": [{"voucher_date": {"$gte": start, "$lte": end}},
                                                                    {"account_head": hoa}]})

    for intent in district_destinations:
        district_destinations_array.append(intent)

    raw_district_destinations = json.dumps(district_destinations_array, default=json_util.default)

    return raw_district_destinations


@app.route('/raw_acc_head_balance')
def raw_acc_head_balance():
    loan = []
    loan_dict = Database.find("trailBalance", {})

    for tran in loan_dict:
        loan.append(tran)

    single_loan = json.dumps(loan, default=json_util.default)

    return single_loan


@app.route('/raw_acc_head_opening_balance/<string:hoa>')
def raw_acc_head_opening_balance(hoa):
    loan = []
    loan_dict = Database.find("trailBalance", {"Head of Accounts": hoa})

    for tran in loan_dict:
        loan.append(tran)

    single_loan = json.dumps(loan, default=json_util.default)

    return single_loan


@app.route('/demands_by_cheque/<string:_id>')
def download_receipt_by_cheque(_id):
    email = session['email']
    user = User.get_by_email(email)

    if email is not None:
        return render_template('receipt_download_by_cheque.html', user=user, loan_id=_id)
    else:
        return render_template('login_fail.html', user=user)


@app.route('/mini_demands_by_cheque/<string:_id>')
def download_receipt_by_cheque_minis(_id):
    email = session['email']
    user = User.get_by_email(email)

    if email is not None:
        return render_template('receipt_download_minis_by_cheque.html', user=user, loan_id=_id)
    else:
        return render_template('login_fail.html', user=user)


@app.route('/view_all_demands')
def all_demands_view():
    email = session['email']
    user = User.get_by_email(email)

    if email is not None:
        return render_template('ViewAllDemands.html', user=user)
    else:
        return render_template('login_fail.html', user=user)


@app.route('/view_all_mini_demands')
def all_mini_demands_view():
    email = session['email']
    user = User.get_by_email(email)

    if email is not None:
        return render_template('ViewAllMiniDemands.html', user=user)
    else:
        return render_template('login_fail.html', user=user)


@app.route('/rawDemandsByLoan/<string:loan_id>/<string:ro_number>')
def raw_demands_by_loan_id(loan_id, ro_number):
    loan = []
    loan_dict = Database.find("Demands", {"ann_id": loan_id,
                                          "ro_number": ro_number})

    for tran in loan_dict:
        loan.append(tran)

    single_loan = json.dumps(loan, default=json_util.default)

    return single_loan


@app.route('/rawMinisByDemand/<string:_id>')
def raw_minis_by_demands(_id):
    loan = []
    loan_dict = Database.find("mDemands", {"demand_id": _id})

    for tran in loan_dict:
        loan.append(tran)

    single_loan = json.dumps(loan, default=json_util.default)

    return single_loan


@app.route('/raw_demands')
def get_raw_all_demands():
    all_credit = []
    all_credit_dict = Database.find("Demands", {})
    for tran in all_credit_dict:
        all_credit.append(tran)

    all_credits = json.dumps(all_credit, default=json_util.default)

    return all_credits


@app.route('/raw_mini_demands')
def get_raw_all_mini_demands():
    all_credit = []
    all_credit_dict = Database.find("mDemands", {})
    for tran in all_credit_dict:
        all_credit.append(tran)

    all_credits = json.dumps(all_credit, default=json_util.default)

    return all_credits


@app.route('/raw_demands_by_cheque_number/<string:cheque_number>')
def get_raw_receipt_by_cheque(cheque_number):
    all_credit = []
    all_credit_dict = Database.find("Demands", {"demand_reference": cheque_number})
    for tran in all_credit_dict:
        all_credit.append(tran)

    all_credits = json.dumps(all_credit, default=json_util.default)

    return all_credits


@app.route('/raw_mini_demands_by_cheque_number/<string:cheque_number>')
def get_raw_mini_receipt_by_cheque(cheque_number):
    all_credit = []
    all_credit_dict = Database.find("mDemands", {"demand_reference": cheque_number})
    for tran in all_credit_dict:
        all_credit.append(tran)

    all_credits = json.dumps(all_credit, default=json_util.default)

    return all_credits


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


@app.route('/delete_demand/<string:_id>')
def delete_demand(_id):
    email = session['email']
    user = User.get_by_email(email)

    Demand.deletefrom_mongo(_id=_id)

    return render_template('deleted.html', user=user)


@app.route('/Credit')
def get_credits():
    all_credit = []
    all_credit_dict = Database.find("accounts", {'nature_of_transaction': "Credit"})
    for tran in all_credit_dict:
        all_credit.append(tran)

    all_credits = json.dumps(all_credit, default=json_util.default)

    return all_credits


@app.route('/multi_ledger_raw')
def get_multi_ledgers():
    all_credit = []
    all_credit_dict = Database.find("accounts", {'nature_of_transaction': "Multi-Ledger"})
    for tran in all_credit_dict:
        all_credit.append(tran)

    all_credits = json.dumps(all_credit, default=json_util.default)

    return all_credits


@app.route('/inside_multi_ledger_raw/<string:voucher_id>')
def get_raw_multi_ledgers(voucher_id):
    all_credit = []
    all_credit_dict = Database.find("accounts", {'payment_voucher': voucher_id})
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


@app.route('/RawLoanApplications/SeatWise/<string:profile>')
def raw_all_applications_seat_wise(profile):
    all_loans = []

    stat = profile.replace("_", " ")

    all_loans_dict = Database.find("loans", {"user_name": stat})
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


@app.route('/demand_ann_id/<string:ann_id>/<string:demand_number>')
def get_demand_by_ann_id(ann_id, demand_number):
    loan = []
    loan_dict = Database.find("Demands", {"ann_id": ann_id,
                                          "demand_number": demand_number})
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


@app.route('/getLoansByIdentfiernRO/<string:ann_loan_id>/<string:ro_number>')
def get_applications_by_identifier_ro(ann_loan_id, ro_number):
    loan = []

    loan_dict = Database.find("loans", {"ann_loan_id": ann_loan_id,
                                        "ro_number": ro_number})

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


@app.route('/Multi_Ledger_View')
def multi_ledger_view():
    email = session['email']
    user = User.get_by_email(email)

    if email is not None:
        return render_template('multi_ledger_View.html', user=user)
    else:
        return render_template('login_fail.html', user=user)


@app.route('/ViewInsideLedger/<string:voucher_id>')
def inside_multi_ledger_view(voucher_id):
    email = session['email']
    user = User.get_by_email(email)

    if email is not None:
        return render_template('inside_multi_ledger_View.html', user=user, voucher_id=voucher_id)
    else:
        return render_template('login_fail.html', user=user)


@app.route('/ViewAllLoanApplications/<string:profile>')
def all_loans_view(profile):
    email = session['email']
    user = User.get_by_email(email)

    if email is not None:
        return render_template('ViewLoans.html', user=user, profile=profile)
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
