from google import genai
import os
import json
import requests
import warnings
from bs4 import BeautifulSoup


# =========================================================
# AYARLAR
# =========================================================

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

BASE_URL = "https://www.ilan.gov.tr"
API_URL = "https://www.ilan.gov.tr/api/api/services/app/Ad/AdsByFilter"

warnings.filterwarnings(
    "ignore",
    message="Unverified HTTPS request"
)


# =========================================================
# GEMINI
# =========================================================

gemini = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# HTTP SESSION
# =========================================================

session = requests.Session()

session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": BASE_URL,
    "Referer": BASE_URL + "/",
    "X-Requested-With": "XMLHttpRequest",
    "X-Request-Origin": "IGT-UI",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
})


# =========================================================
# TELEGRAM
# =========================================================

def telegram(msg):

    try:

        r = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            params={
                "chat_id": CHAT_ID,
                "text": msg
            },
            timeout=30
        )

        print(
            "Telegram status:",
            r.status_code
        )

        if r.status_code != 200:
            print(
                "Telegram cevap:",
                r.text[:500]
            )

    except Exception as e:

        print(
            "Telegram hata:",
            e
        )


# =========================================================
# SEEN DOSYASI
# =========================================================

def load_seen():

    try:

        with open(
            "seen.json",
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

            if not isinstance(data, dict):
                raise ValueError(
                    "seen.json beklenen formatta değil."
                )

            return data

    except Exception as e:

        print(
            "seen.json okunamadı:",
            e
        )

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


# =========================================================
# ANA SITE TEST
# =========================================================

def test_site():

    print(
        "======================================"
    )

    print(
        "ilan.gov.tr bağlantı testi"
    )

    print(
        "======================================"
    )

    try:

        r = session.get(
            BASE_URL + "/",
            verify=False,
            timeout=60
        )

        print(
            "ANA SITE STATUS:",
            r.status_code
        )

        print(
            "ANA SITE CONTENT TYPE:",
            r.headers.get("content-type")
        )

        if r.status_code != 200:

            print(
                "ANA SITE UYARI:",
                r.text[:500]
            )

            return False

        return True

    except Exception as e:

        print(
            "ANA SITE TEST HATASI:",
            e
        )

        return False


# =========================================================
# API İSTEĞİ
# =========================================================

def get_ads(payload, kaynak):

    print(
        "======================================"
    )

    print(
        f"{kaynak} API isteği başlıyor"
    )

    print(
        "======================================"
    )

    try:

        r = session.post(
            API_URL,
            json=payload,
            verify=False,
            timeout=60
        )

    except Exception as e:

        print(
            f"{kaynak} API bağlantı hatası:",
            e
        )

        return []


    print(
        f"{kaynak} HTTP STATUS:",
        r.status_code
    )

    print(
        f"{kaynak} CONTENT TYPE:",
        r.headers.get("content-type")
    )

    print(
        f"{kaynak} RESPONSE:",
        r.text[:1000]
    )


    # -----------------------------------------------------
    # HTTP HATA KONTROLÜ
    # -----------------------------------------------------

    if r.status_code != 200:

        print(
            f"{kaynak} API HTTP HATASI:",
            r.status_code
        )

        return []


    # -----------------------------------------------------
    # JSON KONTROLÜ
    # -----------------------------------------------------

    try:

        data = r.json()

    except ValueError:

        print(
            f"{kaynak} API JSON döndürmedi."
        )

        print(
            "Gelen cevap:",
            r.text[:2000]
        )

        return []


    # -----------------------------------------------------
    # RESULT / ADS KONTROLÜ
    # -----------------------------------------------------

    try:

        ads = data["result"]["ads"]

    except (
        KeyError,
        TypeError
    ):

        print(
            f"{kaynak} API cevabında "
            "'result.ads' bulunamadı."
        )

        print(
            "Gelen JSON:"
        )

        print(
            json.dumps(
                data,
                ensure_ascii=False,
                indent=2
            )[:3000]
        )

        return []


    if not isinstance(
        ads,
        list
    ):

        print(
            f"{kaynak} API 'ads' listesi beklenen formatta değil."
        )

        return []


    print(
        f"{kaynak} toplam ilan:",
        len(ads)
    )

    return ads


# =========================================================
# İFLAS İLANLARI
# =========================================================

def get_iflas():

    payload = {

        "keys": {

            "aci": [62],

            "txv": [12]

        },

        "skipCount": 0,

        "maxResultCount": 20

    }

    return get_ads(
        payload,
        "İFLAS"
    )


# =========================================================
# İFLAS DETAY
# =========================================================

def get_iflas_detay(ad_id):

    url = (
        "https://www.ilan.gov.tr/api/api/services/app/"
        f"AdDetail/GetAdDetail?id={ad_id}"
    )

    try:

        r = session.get(
            url,
            verify=False,
            timeout=60
        )

    except Exception as e:

        print(
            "İflas detay bağlantı hatası:",
            e
        )

        return {}


    print(
        "İflas detay status:",
        r.status_code
    )


    if r.status_code != 200:

        print(
            "İflas detay HTTP hatası:",
            r.status_code
        )

        return {}


    try:

        data = r.json()

    except ValueError:

        print(
            "İflas detay JSON döndürmedi."
        )

        print(
            r.text[:1000]
        )

        return {}


    try:

        return data["result"]

    except (
        KeyError,
        TypeError
    ):

        print(
            "İflas detay result bulunamadı."
        )

        return {}


# =========================================================
# GEMINI MODEL TEST
# =========================================================

def test_gemini():

    try:

        models = gemini.models.list()

        for m in models:

            print(
                m.name
            )

    except Exception as e:

        print(
            "MODEL LISTE HATASI:",
            e
        )


# =========================================================
# GEMINI ÖZET
# =========================================================

def yapay_zeka_ozetle(metin):

    try:

        cevap = gemini.models.generate_content(

            model="gemini-3.5-flash",

            contents=f"""
Aşağıdaki iflas veya konkordato ilanını özetle.

Kurallar:

- Düz metin yaz.
- Markdown kullanma.
- ** kullanma.
- * kullanma.
- # kullanma.
- Emoji kullanma.
- Açıklama yapma.
- En fazla 500 karakter kullan.

Format:

Karar:
Mahkeme:
İlgili:
Özet:
Sonuç:

İlan:

{metin}
"""
        )

        return cevap.text

    except Exception as e:

        print(
            "Gemini hata:",
            e
        )

        return metin[:1000]


# =========================================================
# PERSONEL
# =========================================================

def get_personel():

    payload = {

        "keys": {

            "aci": [62],

            "txv": [8]

        },

        "skipCount": 0,

        "maxResultCount": 20

    }

    return get_ads(
        payload,
        "PERSONEL"
    )


# =========================================================
# PROGRAM
# =========================================================

print(
    "======================================"
)

print(
    "KONYA İLAN TAKİP BAŞLIYOR"
)

print(
    "======================================"
)


# ---------------------------------------------------------
# SITE TEST
# ---------------------------------------------------------

test_site()


# ---------------------------------------------------------
# SEEN
# ---------------------------------------------------------

seen = load_seen()


# =========================================================
# İFLAS
# =========================================================

iflaslar = get_iflas()

old_iflas = {
    str(x)
    for x in seen.get(
        "iflas",
        []
    )
}

print(
    "İflas ilan sayısı:",
    len(iflaslar)
)

print(
    "Seen iflas:",
    len(old_iflas)
)


new_iflas_ids = set()


for ilan in iflaslar:

    uid = str(
        ilan.get(
            "id",
            ""
        )
    )

    if not uid:
        continue

    new_iflas_ids.add(
        uid
    )

    if uid not in old_iflas:

        print(
            "Yeni iflas ilanı:",
            ilan.get(
                "title",
                ""
            )
        )

        link = (
            BASE_URL
            + ilan.get(
                "urlStr",
                ""
            )
        )


        try:

            detay = get_iflas_detay(
                uid
            )

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

            ozet = yapay_zeka_ozetle(
                temiz[:15000]
            )

        except Exception as e:

            print(
                "Detay okunamadı:",
                e
            )

            ozet = (
                "Özet alınamadı."
            )


        telegram(

            f"⚖️ Yeni İflas Hukuku İlanı\n\n"

            f"📌 {ilan.get('title', '')}\n\n"

            f"🏛 {ilan.get('advertiserName', '')}\n\n"

            f"📝 Özet:\n{ozet}\n\n"

            f"📄 İlan No:\n"
            f"{ilan.get('adNo', '')}\n\n"

            f"🔗 {link}"

        )


# ---------------------------------------------------------
# GEÇMİŞİ KORU
# ---------------------------------------------------------

seen["iflas"] = sorted(
    old_iflas.union(
        new_iflas_ids
    )
)


# =========================================================
# PERSONEL
# =========================================================

personeller = get_personel()

old_personel = {
    str(x)
    for x in seen.get(
        "personel",
        []
    )
}

print(
    "Personel ilan sayısı:",
    len(personeller)
)

print(
    "Seen personel:",
    len(old_personel)
)


new_personel_ids = set()


for ilan in personeller:

    uid = str(
        ilan.get(
            "id",
            ""
        )
    )

    if not uid:
        continue

    new_personel_ids.add(
        uid
    )

    if uid not in old_personel:

        print(
            "Yeni personel ilanı:",
            ilan.get(
                "title",
                ""
            )
        )

        link = (
            BASE_URL
            + ilan.get(
                "urlStr",
                ""
            )
        )


        telegram(

            f"👨‍💼 Yeni Personel Alımı\n\n"

            f"{ilan.get('title', '')}\n\n"

            f"Kurum:\n"
            f"{ilan.get('advertiserName', '')}\n\n"

            f"İlan No:\n"
            f"{ilan.get('adNo', '')}\n\n"

            f"{link}"

        )


# ---------------------------------------------------------
# GEÇMİŞİ KORU
# ---------------------------------------------------------

seen["personel"] = sorted(
    old_personel.union(
        new_personel_ids
    )
)


# =========================================================
# KAYDET
# =========================================================

save_seen(
    seen
)


print(
    "======================================"
)

print(
    "TAMAMLANDI"
)

print(
    "======================================"
)
