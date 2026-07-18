import os
import json
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

BASE_URL = "https://www.ilan.gov.tr"

def telegram(msg):
requests.get(
f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
params={
"chat_id": CHAT_ID,
"text": msg
},
timeout=30
)

def load_seen():
try:
with open("seen.json", "r", encoding="utf-8") as f:
return json.load(f)
except:
return {
"iflas": [],
"personel": []
}

def save_seen(data):
with open("seen.json", "w", encoding="utf-8") as f:
json.dump(data, f, ensure_ascii=False, indent=2)

def get_iflas():
url = "https://www.ilan.gov.tr/api/api/services/app/Ad/AdsByFilter"

payload = {
    "keys": {
        "aci": [62],
        "txv": [12]
    },
    "skipCount": 0,
    "maxResultCount": 20
}

r = requests.post(
    url,
    json=payload,
    headers={"User-Agent": "Mozilla/5.0"},
    verify=False,
    timeout=60
)

return r.json()["result"]["ads"]

def get_personel():
url = "https://www.ilan.gov.tr/api/api/services/app/Ad/AdsByFilter"

payload = {
    "keys": {
        "aci": [62],
        "txv": [3]
    },
    "skipCount": 0,
    "maxResultCount": 20
}

r = requests.post(
    url,
    json=payload,
    headers={"User-Agent": "Mozilla/5.0"},
    verify=False,
    timeout=60
)

return r.json()["result"]["ads"]

seen = load_seen()

İFLAS

iflaslar = get_iflas()

old_iflas = set(seen["iflas"])

for ilan in iflaslar:

uid = ilan["id"]

if uid not in old_iflas:

    link = BASE_URL + ilan["urlStr"]

    telegram(
        f"⚖️ Yeni İflas Hukuku İlanı\n\n"
        f"{ilan['title']}\n\n"
        f"Mahkeme:\n{ilan['advertiserName']}\n\n"
        f"İlan No:\n{ilan['adNo']}\n\n"
        f"{link}"
    )

seen["iflas"] = [x["id"] for x in iflaslar]

PERSONEL

personeller = get_personel()

old_personel = set(seen["personel"])

for ilan in personeller:

uid = ilan["id"]

if uid not in old_personel:

    link = BASE_URL + ilan["urlStr"]

    telegram(
        f"👨‍💼 Yeni Personel Alımı\n\n"
        f"{ilan['title']}\n\n"
        f"Kurum:\n{ilan['advertiserName']}\n\n"
        f"İlan No:\n{ilan['adNo']}\n\n"
        f"{link}"
    )

seen["personel"] = [x["id"] for x in personeller]

save_seen(seen)

print("Tamamlandi")
