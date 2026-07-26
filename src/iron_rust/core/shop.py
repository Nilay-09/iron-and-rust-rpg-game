"""
Town shops — buy weapons and items, sell surplus. Prices scale with charisma
(Task 6): a silver tongue buys cheaper and sells dearer. Listings are sorted by
value (Task 20).
"""

import math

from iron_rust.data.items import ITEMS
from iron_rust.data.towns import TOWNS
from iron_rust.data.weapons import WEAPONS
from iron_rust.ui.dialogue import Dialogue, console

SELL_RATIO = 0.5        # base fraction of value you get back when selling
REFUSE_REP = -30        # town rep at/below this: the shop refuses service (Task 9)
# The combined price modifier is clamped so selling is ALWAYS worse than buying
# (0.5 * (1 + 0.30) = 0.65 < 1 - 0.30 = 0.70) — no buy-low/sell-high arbitrage.
MOD_MIN, MOD_MAX = -0.25, 0.30


def _discount(hero):
    """Charisma (and Doc's arc) shaves off buying / adds to selling."""
    disc = min(0.25, hero.stat("charisma") * 0.02)
    if hero.has_bonus("shop_discount"):      # Doc's companion arc
        disc += 0.10
    return disc


def _town_factor(hero, town):
    """Task 9: townsfolk reputation shifts prices in that specific town."""
    if not town:
        return 0.0
    rep = hero.town_reputation(town)
    return max(-0.25, min(0.25, rep * 0.01))     # +rep -> cheaper, -rep -> dearer


def _price_mod(hero, town):
    """Combined, clamped price modifier used for both buying and selling."""
    return max(MOD_MIN, min(MOD_MAX, _discount(hero) + _town_factor(hero, town)))


def buy_price(hero, base, town=None):
    # Round buying UP and selling DOWN so sell is always strictly below buy —
    # even after rounding on cheap items — leaving no buy-low/sell-high margin.
    return max(1, math.ceil(base * (1 - _price_mod(hero, town))))


def sell_price(hero, base, town=None):
    return max(1, math.floor(base * SELL_RATIO * (1 + _price_mod(hero, town))))


def _buy(hero, shop, dialogue, town=None):
    # Build a sorted stock list: (key, kind, display_name, base_price).
    stock = []
    for wk in shop.get("weapons", []):
        stock.append((wk, "weapon", WEAPONS[wk]["name"], WEAPONS[wk]["price"]))
    for ik in shop.get("items", []):
        stock.append((ik, "item", ITEMS[ik]["name"], ITEMS[ik]["price"]))
    # Task 20: sort by price, then name.
    stock = sorted(stock, key=lambda s: (s[3], s[2]))

    labels, options = {}, []
    for key, kind, name, base in stock:
        price = buy_price(hero, base, town)
        extra = f"dmg {WEAPONS[key]['damage']}" if kind == "weapon" else ITEMS[key]["desc"]
        tag = "" if hero.money >= price else "  (can't afford)"
        opt = f"{kind}:{key}"
        options.append(opt)
        labels[opt] = f"${price:>4}  {name} — {extra}{tag}"
    BACK = "__back__"
    options.append(BACK)
    labels[BACK] = "Back"

    choice = dialogue.choose("Buy what?", options, labels=labels)
    if choice == BACK:
        return

    kind, key = choice.split(":", 1)
    base = WEAPONS[key]["price"] if kind == "weapon" else ITEMS[key]["price"]
    price = buy_price(hero, base, town)
    if hero.money < price:
        dialogue.narrator("You can't cover that.")
        dialogue.pause(0.5)
        return

    hero.money -= price
    if kind == "weapon":
        hero.equip_weapon(key)
        dialogue.success(f"Bought & equipped {WEAPONS[key]['name']} for ${price}.")
    else:
        hero.add_item(key)
        dialogue.success(f"Bought {ITEMS[key]['name']} for ${price}.")
    dialogue.pause(0.5)


def _sell(hero, dialogue, town=None):
    owned = [(k, c) for k, c in hero.consumables.items() if c > 0]
    if not owned:
        dialogue.narrator("You've nothing worth selling.")
        dialogue.pause(0.5)
        return

    # Task 20: sort by sell value, highest first.
    owned = sorted(owned, key=lambda kc: ITEMS[kc[0]]["price"], reverse=True)

    labels, options = {}, []
    for key, count in owned:
        price = sell_price(hero, ITEMS[key]["price"], town)
        options.append(key)
        labels[key] = f"${price:>4}  {ITEMS[key]['name']} x{count}"
    BACK = "__back__"
    options.append(BACK)
    labels[BACK] = "Back"

    choice = dialogue.choose("Sell what?", options, labels=labels)
    if choice == BACK:
        return

    price = sell_price(hero, ITEMS[choice]["price"], town)
    hero.consumables[choice] -= 1                  # remove without applying the effect
    if hero.consumables[choice] <= 0:
        del hero.consumables[choice]
    hero.money += price
    dialogue.success(f"Sold {ITEMS[choice]['name']} for ${price}.")
    dialogue.pause(0.5)


def shop_menu(hero, town_key, dialogue=Dialogue):
    """Open the shop for a town, if it has one."""
    town = TOWNS.get(town_key, {})
    shop = town.get("shop")
    if not shop:
        dialogue.narrator("There's no shop worth the name here.")
        dialogue.pause(0.5)
        return

    # Task 9: burn the town badly enough and the shop won't serve you.
    if hero.town_reputation(town_key) <= REFUSE_REP:
        dialogue.narrator(f"The shopkeep spits. \"Your kind isn't welcome in {town['name']}. Get out.\"")
        dialogue.pause(0.7)
        return

    BUY, SELL, LEAVE = "buy", "sell", "leave"
    while True:
        console.print()
        rep = hero.town_reputation(town_key)
        mood = "[green](they like you)[/green]" if rep > 10 else "[red](they distrust you)[/red]" if rep < -10 else ""
        console.print(
            f"[bold khaki1]{shop['name']}[/bold khaki1]   [gold1]Your purse: ${hero.money}[/gold1]   {mood}",
            justify="center",
        )
        choice = dialogue.choose(
            "The shopkeep waits.",
            [BUY, SELL, LEAVE],
            labels={BUY: "Buy", SELL: "Sell", LEAVE: "Leave the shop"},
        )
        if choice == LEAVE:
            return
        if choice == BUY:
            _buy(hero, shop, dialogue, town_key)
        else:
            _sell(hero, dialogue, town_key)
