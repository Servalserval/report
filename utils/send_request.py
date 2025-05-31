import requests

def send_request(url, method, json = None, header = None, params = None, timeout = None):
    if method == "get":
        try:
            response = requests.get(url = url, params=params, timeout=timeout, headers=header)
            if response.ok:
                return response.json()
            else:
                print("Error : ", response)
                return
        except Exception as e:
            print(e)
    if method == "post":
        try:
            response = requests.post(url = url, json = json, headers=header, timeout=timeout)
            return response.json()
        except Exception as e:
            print(e)