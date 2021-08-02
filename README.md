# psp-web-app

A simple web application that consumes the PSP Reporting API

Heroku: https://psp-web-app.herokuapp.com/login

# Important Notes

- I didn't use logger because heroku can see logs from Python's sys.stdout

- Transaction Report API is not working as expected. It is an MongoDB related error and I can't do anything about it.

  Error message returned from server: "transaction_report: {'code': 9, 'status': 'DECLINED', 'message': "10.72.23.66:27017: The 'cursor' option is required, except   for aggregate with the explain argument"}"
  
  Related Links I found:
  
  https://stackoverflow.com/questions/43955950/mongodb-error-the-cursor-option-is-required-except-for-aggregation-explain
  
  https://github.com/TylerBrock/mongo-hacker/issues/182
