from decouple import config
import requests
from fastapi.exceptions import HTTPException
import json
import uuid

class WiseService:
    def __init__(self):
        self.main_url = config("WISE_URL")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config('WISE_TOKEN')}"
        }
        self.profile_id = self._get_profile_id()

    def _get_profile_id(self):
        url = f"{self.main_url}/v1/profiles"
        resp = requests.get(url, headers=self.headers)

        if resp.status_code == 200:
            resp = resp.json()
            return [el["id"] for el in resp if el["type"] == "personal"][0]
        raise HTTPException(500, "Payment provider is not available")

    def create_quote(self, amount):
        url = f"{self.main_url}/v2/quotes"
        data = {
            "sourceCurrency": "EUR",
            "targetCurrency": "EUR",
            "targetAmount": amount,
            "profile": self.profile_id
        }
        resp = requests.post(url, headers=self.headers, data=json.dumps(data))

        if resp.status_code == 200:
            resp = resp.json()
            return resp["id"]
        raise HTTPException(500, "Payment provider is not available at the moment")


    def create_recipient_account(self, full_name, iban):
        url = self.main_url + "/v1/accounts"
        data = { 
          "currency": "EUR", 
          "type": "iban", 
          "profile": self.profile_id, 
          "accountHolderName": full_name,
          "legalType": "PRIVATE",
           "details": { 
              "iban": iban,
           }
        }
        resp = requests.post(url, headers=self.headers,data=json.dumps(data))
        if resp.status_code == 200:
            resp = resp.json()
            return resp["id"]
        raise HTTPException(500, "Payment provider is not available at the moment")

    def create_transfer(self, target_account_id, quote_id):
        customer_transaction_id = str(uuid.uuid4())
        url = self.main_url + "/v1/transfers"
        data = {
            "targetAccount": target_account_id,   
            "quoteUuid": quote_id,
            "customerTransactionId": customer_transaction_id,
        }
        resp = requests.post(url, headers=self.headers, data=json.dumps(data))
        if resp.status_code == 200:
            resp = resp.json()
            return resp["id"]
        raise HTTPException(500, "Payment provider is not available at the moment")

    def fund_transfer(self, transfer_id):
        url = self.main_url + f"/v3/profiles/{self.profile_id}/transfers/{transfer_id}/payments"
        data = {
            "type": "BALANCE"
        }
        resp = requests.post(url, headers=self.headers, data=json.dumps(data))
        if resp.status_code == 201:
            resp = resp.json()
            return resp["balanceTransactionId"]
        raise HTTPException(500, "Payment provider is not available at the moment")


if __name__ == "__main__":
    wise = WiseService()
    quote_id = wise.create_quote(23.33)
    recipient_id = wise.create_recipient_account("dimi ggg", "GB29NWBK60161331926819")
    transfer_id = wise.create_transfer(recipient_id, quote_id)
    res = wise.fund_transfer(transfer_id)
    a = 5

