import requests
r = requests.get('http://localhost:8888/generate', json={"data": {"company": "ХУЙ",
                                                                  "product": "ПИЗДА",
                                                                  "date": "11.12.13"}})
print(r.status_code)
print(r.json())
