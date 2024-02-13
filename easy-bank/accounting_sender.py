import requests

class AccountingSender:
    def __init__(self, base_url):
        self.base_url = base_url

    def send_accounting_data(self, accounting_data):
        endpoint = f"{self.base_url}/accounting"
        print("posting to: ", endpoint)
        headers = {"Content-Type": "application/json"}
        payload = []
        for entry in accounting_data:
            payload.append(dict(entry))
        response = requests.post(endpoint, json=payload, headers=headers)
        if response.status_code == 201:
            print(f"Accounting entry added successfully:: {response.json()}")
        else:
            print(f"Failed to add accounting entry: {response.json()}")
