import json
import urllib.request

url = 'http://127.0.0.1:8000/predict'
data = {
    "Gender": "Male",
    "Married": "Yes",
    "Dependents": "0",
    "Education": "Graduate",
    "Self_Employed": "No",
    "ApplicantIncome": 5720,
    "CoapplicantIncome": 0,
    "LoanAmount": 110,
    "Loan_Amount_Term": 360.0,
    "Credit_History": 1,
    "Property_Area": "Urban",
}
req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    print(resp.read().decode())
