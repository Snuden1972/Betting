import itertools


def calculate_payout(stake_per_bet, odds_list):
    total_odds = 1
    for odds in odds_list:
        total_odds *= odds
    return stake_per_bet * total_odds


# ---------------- ACCA ----------------
def resolve_acca(stake, odds_list, results):
    if all(results):
        return calculate_payout(stake, odds_list)
    return 0


# ---------------- SYSTEM ----------------
def resolve_system(stake, odds_list, results, min_required):
    """
    Rigtig system-bet:
    - laver kombinationer
    - evaluerer hver kombination
    """

    indices = list(range(len(odds_list)))

    combinations = list(itertools.combinations(indices, min_required))

    stake_per_bet = stake / len(combinations)

    total_payout = 0

    for combo in combinations:
        combo_odds = []
        combo_results = []

        for i in combo:
            combo_odds.append(odds_list[i])
            combo_results.append(results[i])

        # alle i combo skal være rigtige
        if all(combo_results):
            total_payout += calculate_payout(stake_per_bet, combo_odds)

    return total_payout


# ---------------- TEST ----------------

stake = 10
odds = [1.5, 2.0, 2.5, 1.8]

# 3 rigtige, 1 forkert
results = [True, True, False, True]

print("ACCA:", resolve_acca(stake, odds[:3], results[:3]))

print("SYSTEM 3/4:", resolve_system(stake, odds, results, 3))