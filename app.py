import os
import json
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

BASE_URL = "https://www.ilan.gov.tr"


def telegram(msg):

    r = requests.get(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        params={
            "chat_id": CHAT_ID,
            "text": msg
        },
        timeout=30
    )

    print("Telegram status:", r.status_code)


def load_seen():

    try:

        with open(
            "seen.json",
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except:

        return {
            "iflas": [],
            "personel": []
        }


def save_seen(data):

    with open(
        "seen.json",
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )


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
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        verify=False,
        timeout=60
    )

    return r.json()["result"]["ads"]


def get_iflas_detay(ad_id):

    url = (
        "https://www.ilan.gov.tr/api/api/services/app/"
        f"AdDetail/GetAdDetail?id={ad_id}"
    )

    r = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "X-Requested-With": "XMLHttpRequest",
            "X-Request-Origin": "IGT-UI"
        },
        verify=False,
        timeout=60
    )

    return r.json()["result"]


def get_personel():

    url = "https://www.ilan.gov.tr/api/api/services/app/Ad/AdsByFilter"

    payload = {
        "keys": {
            "aci": [62],
            "txv": [8]
        },
        "skipCount": 0,
        "maxResultCount": 20
    }

    r = requests.post(
        url,
        json=payload,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        verify=False,
        timeout=60
    )

    return r.json()["result"]["ads"]


seen = load_seen()

iflaslar = get_iflas()

old_iflas = set(
    seen.get(
        "iflas",
        []
    )
)

print("Iflas ilan sayisi:", len(iflaslar))
print("Seen iflas:", len(old_iflas))

for ilan in iflaslar:

    uid = ilan["id"]

    if uid not in old_iflas:

        print(
            "Yeni iflas ilani:",
            ilan["title"]
        )

        link = BASE_URL + ilan["urlStr"]

        try:

            detay = get_iflas_detay(uid)

            html = detay.get(
                "content",
                ""
            )

            temiz = BeautifulSoup(
                html,
                "html.parser"
            ).get_text(
                " ",
                strip=True
            )

            ozet = temiz[:1200]

            if len(temiz) > 1200:
                ozet += "..."

        except Exception as e:

            print(
                "Detay okunamadi:",
                e
            )

            ozet = "Özet alınamadı."

        telegram(
            f"⚖️ Yeni İflas Hukuku İlanı\n\n"
            f"📌 {ilan['title']}\n\n"
            f"🏛 {ilan['advertiserName']}\n\n"
            f"📝 Özet:\n{ozet}\n\n"
            f"📄 İlan No:\n{ilan['adNo']}\n\n"
            f"🔗 {link}"
        )

seen["iflas"] = [
    x["id"]
    for x in iflaslar
]

personeller = get_personel()

old_personel = set(
    seen.get(
        "personel",
        []
    )
)

print(
    "Personel ilan sayisi:",
    len(personeller)
)

print(
    "Seen personel:",
    len(old_personel)
)

for ilan in personeller:

    uid = ilan["id"]

    if uid not in old_personel:

        print(
            "Yeni personel ilani:",
            ilan["title"]
        )

        link = BASE_URL + ilan["urlStr"]

        telegram(
            f"👨‍💼 Yeni Personel Alımı\n\n"
            f"{ilan['title']}\n\n"
            f"Kurum:\n{ilan['advertiserName']}\n\n"
            f"İlan No:\n{ilan['adNo']}\n\n"
            f"{link}"
        )

seen["personel"] = [
    x["id"]
    for x in personeller
]

save_seen(seen)

print("Tamamlandi")
