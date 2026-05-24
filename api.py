from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import itertools
import requests

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- API KEY ----------------
API_KEY = "c2b6umPiI70t8ZQYdC0gMnWPyDdNezHKMnjGSo0wapxCZqykgmiYlgblW52l"


# ---------------- PAYOUT ENGINE ----------------

def calculate_payout(stake, odds_list):
    total = 1
    for o in odds_list:
        total *= o
    return stake * total


def resolve_system(stake, odds_list, results, k):
    indices = list(range(len(odds_list)))
    combos = list(itertools.combinations(indices, k))

    stake_per_bet = stake / len(combos)
    total = 0

    for combo in combos:
        if all(results[i] for i in combo):
            combo_odds = [odds_list[i] for i in combo]
            total += calculate_payout(stake_per_bet, combo_odds)

    return total


# ---------------- MODEL ----------------

class BetRequest(BaseModel):
    bet_type: str
    stake: float
    odds: list[float]
    results: list[bool]
    k: int | None = None


# ---------------- ENDPOINTS ----------------

@app.post("/calculate")
def calculate(data: BetRequest):

    if data.bet_type == "acca":
        if all(data.results):
            return {"payout": calculate_payout(data.stake, data.odds)}
        return {"payout": 0}

    if data.bet_type == "system":
        return {
            "payout": resolve_system(
                data.stake,
                data.odds,
                data.results,
                data.k
            )
        }

    return {"error": "invalid bet type"}


@app.get("/odds")
def get_odds():
    return {"odds": [1.85, 4.33, 3.50]}


# ---------------- SPORTMONKS CLEAN FEED ----------------

@app.get("/coupons")
def get_coupons():

    url = "https://api.sportmonks.com/v3/football/odds/pre-match"

    params = {
        "api_token": API_KEY,
        "bookmakers": "2",
        "markets": "1",
        "include": "fixture,bookmakers,bookmakers.markets,bookmakers.markets.selections",
        "per_page": 10
    }

    r = requests.get(url, params=params)
    data = r.json()

    coupons = []

    for item in data.get("data", []):

        fixture = item.get("fixture", {})
        match_name = fixture.get("name")

        home = draw = away = None

        bookmakers = item.get("bookmakers", [])

        for b in bookmakers:
            for market in b.get("markets", []):
                for sel in market.get("selections", []):

                    name = sel.get("name")
                    odd = sel.get("odd") or sel.get("value")

                    if name == "1":
                        home = odd
                    elif name == "X":
                        draw = odd
                    elif name == "2":
                        away = odd

        # kun tilføj hvis vi faktisk har odds
        if match_name and (home or draw or away):
            coupons.append({
                "match": match_name,
                "home": home,
                "draw": draw,
                "away": away
            })

    return {"coupons": coupons}