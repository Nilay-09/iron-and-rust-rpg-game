# Weapons: damage range (low, high), accuracy modifier added to aim, a tier
# (roughly how strong), and a price for buying at shops. Tier 1 is the starter.
WEAPONS = {
    "basic_pistol": {
        "name": "Worn Pistol",
        "damage": (6, 10),
        "accuracy": 0,
        "tier": 1,
        "price": 0,       # starter — not really for sale
    },
    "revolver": {
        "name": "Six-Shooter",
        "damage": (9, 15),
        "accuracy": 1,
        "tier": 2,
        "price": 120,
    },
    "rifle": {
        "name": "Repeater Rifle",
        "damage": (13, 21),
        "accuracy": 2,     # accurate at range
        "tier": 3,
        "price": 260,
    },
    "shotgun": {
        "name": "Sawed-Off Shotgun",
        "damage": (18, 30),
        "accuracy": -2,    # brutal up close, wild at range
        "tier": 3,
        "price": 300,
    },
}

# What the Hero starts with.
DEFAULT_WEAPON = "basic_pistol"
