import os
import re
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

APIFY_TOKEN = os.getenv("APIFY_TOKEN", "").strip()
APIFY_ACTOR_ID = os.getenv("APIFY_ACTOR_ID", "gocreative.ai~instagram-profile-scraper").strip()
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "").strip()

STATE_NAMES = {
    "AC":"Acre","AL":"Alagoas","AP":"Amapá","AM":"Amazonas","BA":"Bahia","CE":"Ceará",
    "DF":"Distrito Federal","ES":"Espírito Santo","GO":"Goiás","MA":"Maranhão","MT":"Mato Grosso",
    "MS":"Mato Grosso do Sul","MG":"Minas Gerais","PA":"Pará","PB":"Paraíba","PR":"Paraná",
    "PE":"Pernambuco","PI":"Piauí","RJ":"Rio de Janeiro","RN":"Rio Grande do Norte",
    "RS":"Rio Grande do Sul","RO":"Rondônia","RR":"Roraima","SC":"Santa Catarina",
    "SP":"São Paulo","SE":"Sergipe","TO":"Tocantins"
}

def clean_handle(value):
    value = (value or "").strip()
    value = re.sub(r"^https?://(www\.)?instagram\.com/", "", value, flags=re.I)
    value = value.lstrip("@")
    value = re.split(r"[/?#]", value)[0]
    if not re.fullmatch(r"[A-Za-z0-9._]{1,30}", value or ""):
        raise ValueError("Digite um @ do Instagram válido.")
    return value

def pick(obj, *names, default=None):
    for n in names:
        if isinstance(obj, dict) and obj.get(n) not in (None, "", [], {}):
            return obj.get(n)
    return default

def instagram_profile(handle):
    if not APIFY_TOKEN:
        raise RuntimeError("APIFY_TOKEN não configurado.")

    url = f"https://api.apify.com/v2/actors/{APIFY_ACTOR_ID}/run-sync-get-dataset-items"
    payload = {"usernames": [handle], "resultsLimit": 0, "proxyType": "auto"}
    r = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {APIFY_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        json=payload,
        timeout=180
    )
    r.raise_for_status()
    data = r.json()
    if isinstance(data, dict):
        items = data.get("items") or data.get("data") or [data]
    else:
        items = data
    if not items:
        raise LookupError("Perfil não encontrado.")
    item = items[0] if isinstance(items[0], dict) else {}

    return {
        "username": pick(item, "username", default=handle),
        "full_name": pick(item, "full_name", "fullName", "name", default=""),
        "biography": pick(item, "biography", "bio", default=""),
        "email": pick(item, "email", "business_email", "public_email", "publicEmail"),
        "phone": pick(item, "phone", "phone_normalized", "business_phone", "public_phone", "public_phone_number"),
        "website": pick(item, "external_url", "website", "externalUrl"),
        "category": pick(item, "business_category", "category_name", "category"),
        "is_business": bool(pick(item, "is_business", "isBusiness", default=False)),
        "is_verified": bool(pick(item, "is_verified", "verified", default=False))
    }

def google_places_search(name, state, city=None):
    if not GOOGLE_PLACES_API_KEY:
        raise RuntimeError("GOOGLE_PLACES_API_KEY não configurada.")

    uf = (state or "").strip().upper()
    state_label = STATE_NAMES.get(uf, state.strip())
    location_text = ", ".join([x for x in [city.strip() if city else "", state_label, "Brasil"] if x])
    query = f"{name} {location_text}".strip()

    url = "https://places.googleapis.com/v1/places:searchText"
    field_mask = ",".join([
        "places.id",
        "places.displayName",
        "places.formattedAddress",
        "places.nationalPhoneNumber",
        "places.internationalPhoneNumber",
        "places.websiteUri",
        "places.googleMapsUri",
        "places.businessStatus",
        "places.primaryTypeDisplayName"
    ])
    r = requests.post(
        url,
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
            "X-Goog-FieldMask": field_mask
        },
        json={
            "textQuery": query,
            "languageCode": "pt-BR",
            "regionCode": "BR",
            "pageSize": 10
        },
        timeout=40
    )
    r.raise_for_status()
    data = r.json()

    results = []
    for p in data.get("places", []):
        results.append({
            "id": p.get("id"),
            "name": (p.get("displayName") or {}).get("text"),
            "address": p.get("formattedAddress"),
            "phone": p.get("nationalPhoneNumber"),
            "international_phone": p.get("internationalPhoneNumber"),
            "website": p.get("websiteUri"),
            "maps_url": p.get("googleMapsUri"),
            "status": p.get("businessStatus"),
            "type": (p.get("primaryTypeDisplayName") or {}).get("text")
        })
    return query, results

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/health")
def health():
    return jsonify({"ok": True})

@app.post("/api/search")
def search():
    body = request.get_json(silent=True) or {}
    try:
        handle = clean_handle(body.get("handle", ""))
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    state = (body.get("state") or "").strip()
    city = (body.get("city") or "").strip()
    if not state:
        return jsonify({"ok": False, "error": "Informe o estado."}), 400

    try:
        profile = instagram_profile(handle)
    except Exception as e:
        return jsonify({"ok": False, "error": f"Não foi possível consultar o Instagram: {e}"}), 502

    name = (profile.get("full_name") or "").strip()
    if not name:
        return jsonify({"ok": False, "error": "O perfil não informou um nome público para usar na busca."}), 404

    try:
        query, places = google_places_search(name, state, city)
    except Exception as e:
        return jsonify({"ok": False, "error": f"Não foi possível consultar o Google Places: {e}"}), 502

    return jsonify({
        "ok": True,
        "profile": profile,
        "google_query": query,
        "matches": places
    })
