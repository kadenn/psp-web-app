from flask import Flask, render_template, redirect, request, session
from flask_session import Session
import requests
from requests.exceptions import HTTPError

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

test_url = 'https://sandbox-reporting.rpdpymnt.com/api/v3'
live_url = 'https://reporting.rpdpymnt.com/api/v3'
base_url = test_url


@app.route("/")
def index():
  # check if the users exist or not
    if not session.get("email_address"):
        # if not there in the session then redirect to the login page
        return redirect("/login")
    return render_template('index.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email_address = request.form.get("email_address")
        session["email_address"] = email_address

        # initialize token
        get_access_token(email_address, request.form.get("password"))

        if session["token"] is None:
            return render_template("login.html", error='You have entered an invalid email or password')
        else:
            # redirect to the main page
            return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session["email_address"] = None
    session["token"] = None
    return redirect("/")


@app.route("/transaction-query", methods=["POST", "GET"])
def transaction_query():
    if request.method == "POST":
        print('Making transaction query...')

        fromDate = request.form.get("start-date")
        toDate = request.form.get("end-date")
        status = request.form.get("status")
        operation = request.form.get("operation​​")
        merchantId = request.form.get("merchant-id", type=int)
        acquirerId = request.form.get("acquirer-id", type=int)
        paymentMethod = request.form.get("payment-method")
        errorCode = request.form.get("error-code")
        filterField = request.form.get("filter-field​​")
        filterValue = request.form.get("filter-value")

        page_url = request.form.get("page")
        if(page_url == "next_page"):
            session["current_page"] += 1
        elif(page_url == "prev_page"):
            session["current_page"] -= 1

        if session["transaction_query_parameters"] is None:
            parameters = {'fromDate': fromDate, 'toDate': toDate, 'status': status, 'operation': operation, 'merchantId': merchantId, 'acquirerId': acquirerId,
                          'paymentMethod': paymentMethod, 'errorCode': errorCode, 'filterField': filterField, 'filterValue': filterValue}
            session["transaction_query_parameters"] = parameters
        else:
            parameters = session["transaction_query_parameters"]

        transactions = send_post_request(
            f'/transaction/list/?page={session["current_page"]}', parameters)
        if transactions == 'expired_token':
            session["email_address"] = None
            session["token"] = None
            return redirect("/")
        elif not transactions:
            print('An error occurred while making the transaction query.')
            return render_template("transaction-query.html", error='An error occurred while making the transaction query.')

        session["current_page"] = transactions.get('current_page')

        return render_template("transaction-query.html", data=transactions.get('data'), next_page=transactions.get('next_page_url'), prev_page=transactions.get('prev_page_url'))
    session["current_page"] = 1
    session["transaction_query_parameters"] = None
    return render_template("transaction-query.html")


@app.route("/transaction-report", methods=["POST", "GET"])
def transaction_report():
    if request.method == "POST":
        print('Getting transaction report...')

        fromDate = request.form.get("start-date")
        toDate = request.form.get("end-date")
        merchant = request.form.get("merchant-id", type=int)
        acquirer = request.form.get("acquirer-id", type=int)

        if(fromDate is None or toDate is None):
            return render_template("transaction-report.html", error='The fromDate and toDate parameters are required to get a transaction report.')

        parameters = {'fromDate': fromDate, 'toDate': toDate,
                      'merchant': merchant, 'acquirer': acquirer}

        transaction_report = send_post_request(
            '/transactions/report', parameters)
        if transaction_report == 'expired_token':
            session["email_address"] = None
            session["token"] = None
            return redirect("/")
        elif not transaction_report:
            print('An error occurred while retrieving the transaction report.')
            return render_template("transaction-report.html", error='An error occurred while retrieving the transaction report.')

        return render_template("transaction-report.html", data=transaction_report)
    return render_template("transaction-report.html")


@app.route("/get-client", methods=["POST", "GET"])
def get_client():
    if request.method == "POST":
        print('Getting client details...')

        transactionId = request.form.get("transaction-id")
        parameters = {'transactionId': transactionId}
        client_details = send_post_request('/client', parameters)

        if client_details == 'expired_token':
            session["email_address"] = None
            session["token"] = None
            return redirect("/")
        elif not client_details:
            print('An error occurred while getting the client details.')
            return render_template("get-client.html", error='An error occurred while getting the client details.')

        return render_template("get-client.html", data=client_details.get('customerInfo'))
    return render_template("get-client.html")


@app.route("/get-transaction", methods=["POST", "GET"])
def get_transaction():
    if request.method == "POST":
        print('Getting transaction details...')

        transactionId = request.form.get("transaction-id")
        parameters = {'transactionId': transactionId}
        transaction_details = send_post_request('/transaction', parameters)

        if transaction_details == 'expired_token':
            session["email_address"] = None
            session["token"] = None
            return redirect("/")
        elif not transaction_details:
            print('An error occurred while getting the transaction details.')
            return render_template("get-transaction.html", error='An error occurred while getting the transaction details.')

        return render_template("get-transaction.html", data=transaction_details)
    return render_template("get-transaction.html")


def get_access_token(email, password):
    print('Getting new access token...')

    try:
        response = requests.post(base_url + '/merchant/user/login',
                                 data={'email': email, 'password': password})

        # if the response was successful, no Exception will be raised
        response.raise_for_status()
        responseJSON = response.json()

        if(responseJSON.get('status') == "APPROVED"):
            session["token"] = responseJSON.get('token')

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'An error occurred: {err}')


def send_post_request(path, parameters):
    print('Sending post request...')
    response_message = ""

    try:
        # remove keys in dictionary with None values
        cleaned_parameters = {k: v for k, v in parameters.items() if v}
        response = requests.post(base_url + path,
                                 data=cleaned_parameters, headers={'Authorization': session.get("token")})

        responseJSON = response.json()
        response_message = responseJSON.get('message')

        # if the response was successful, no Exception will be raised
        response.raise_for_status()
        return responseJSON

    except HTTPError as http_err:
        if(response_message == 'Token Expired'):
            print("Token expired, user logged out automatically.")
            return 'expired_token'
        else:
            print(
                f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(
            f'An error occurred: {err}')


if __name__ == '__main__':
    app.run(debug=True)
