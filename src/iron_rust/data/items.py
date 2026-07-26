"""
Consumable items — usable in combat and buyable at shops.

type "heal"    -> restores `heal` HP
type "deadeye" -> adds `deadeye` to the Dead Eye meter
"""

ITEMS = {
    "bandage": {
        "name": "Bandage",
        "type": "heal",
        "heal": 15,
        "price": 15,
        "desc": "Stops the bleeding. +15 HP.",
    },
    "whiskey": {
        "name": "Whiskey",
        "type": "heal",
        "heal": 25,
        "price": 25,
        "desc": "Rough medicine, but it works. +25 HP.",
    },
    "medkit": {
        "name": "Field Medkit",
        "type": "heal",
        "heal": 50,
        "price": 60,
        "desc": "Proper doctoring in a tin. +50 HP.",
    },
    "tonic": {
        "name": "Snake-Oil Tonic",
        "type": "deadeye",
        "deadeye": 50,
        "price": 40,
        "desc": "Sharpens the senses something fierce. +50 Dead Eye.",
    },
}
