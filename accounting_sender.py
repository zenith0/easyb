import requests
from datetime import datetime

class AccountingSender:
    def __init__(self, base_url):
        self.base_url = base_url

    def send_accounting_data(self, accounting_data):
        endpoint = f"{self.base_url}/accounting"
        print("posting to: ", endpoint)
        headers = {"Content-Type": "application/json"}
        payload = []
        for fs in accounting_data:
            formatted_entry = {}
            for entry in fs:
                key = entry[0]
                value = entry[1]
                #value = str(entry).split(',') 
            #for key, value in entry.items():
                if key == 'date' or key == 'transaction_date':
                    formatted_entry[key] = value.replace(".", "-").replace("'", "")
                else:
                    formatted_entry[key] = value
            payload.append(dict(formatted_entry))
        print("## Payload: ", payload)
        response = requests.post(endpoint, json=payload, headers=headers)
        if response.status_code == 201:
            print(f"Accounting entry added successfully:: {response.json()}")
        else:
            print(f"Failed to add accounting entry: {response.json()}")

    def send_accounting_total(self, total):
        endpoint = f"{self.base_url}/accounting/total"
        headers = {"Content-Type": "application/json"}
        payload = {'date': datetime.today().strftime("%d-%m-%Y"),
                   'total': total}
        response = requests.post(endpoint, json=payload, headers=headers)
        if response.status_code == 201:
            print(f"Total entry added successfully:: {response.json()}")
        else:
            print(f"Failed to add total entry: {response.json()}")

