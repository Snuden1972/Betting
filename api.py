from fastapi import FastAPI
import requests

app = FastAPI()

API_KEY = "c2b6umPiI70t8ZQYdC0gMnWPyDdNezHKMnjGSo0wapxCZqykgmiYlgblW52l"


@app.get("/")
def home():
    return {"status": "ok"}


@app.get("/coupons")
def get_coupons():

    url = "https://api.sportmonks.com/v3/football/odds/pre-match"

    params = {
        "api_token": API_KEY,
        "include": "fixture,bookmakers,bookmakers.markets,bookmakers.markets.selections",
        "per_page": 50
    }

    r = requests.get(url, params=params)
    data = r.json()

    coupons = []

    for item in data.get("data", []):

        fixture = item.get("fixture", {})
        match_name = fixture.get("name")

        home = draw = away = None

        bookmakers = item.get("bookmakers", [])

        # find bet365 hvis det findes
        for b in bookmakers:
            if b.get("name", "").lower() == "bet365":
                markets = b.get("markets", [])

                for m in markets:
                    for s in m.get("selections", []):

                        name = s.get("name")
                        odd = s.get("odd") or s.get("value")

                        if name == "1":
                            home = odd
                        elif name == "X":
                            draw = odd
                        elif name == "2":
                            away = odd

        # fallback hvis bet365 ikke findes
        if not home and bookmakers:
            b = bookmakers[0]
            for m in b.get("markets", []):
                for s in m.get("selections", []):
                    name = s.get("name")
                    odd = s.get("odd") or s.get("value")

                    if name == "1":
                        home = odd
                    elif name == "X":
                        draw = odd
                    elif name == "2":
                        away = odd

        if match_name and (home or draw or away):
            coupons.append({
                "match": match_name,
                "home": home,
                "draw": draw,
                "away": away
            })

    return {"coupons": coupons}