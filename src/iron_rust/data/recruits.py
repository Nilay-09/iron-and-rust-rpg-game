"""
Recruitable gang members and camp upgrades.

Each recruit is a distinct combat archetype via their `special`:
  cover_fire   - reliable shots at the worst threat
  field_medic  - heals the hero each round
  dynamite     - hits every enemy for a little damage (crowd control)
  sharpshooter - a guaranteed high-damage hit
"""

from iron_rust.entities.npc import NPC

RECRUITS = {
    "eli": {
        "name": "Eli Vance", "age": 34, "gender": "male",
        "role": "backup gunslinger", "special": "cover_fire",
        "loyalty": 70, "hp": 55,
    },
    "doc": {
        "name": "Doc Weller", "age": 51, "gender": "male",
        "role": "field medic", "special": "field_medic",
        "loyalty": 55, "hp": 45,
    },
    "kate": {
        "name": "Dynamite Kate", "age": 29, "gender": "female",
        "role": "demolitionist", "special": "dynamite",
        "loyalty": 45, "hp": 50,
    },
    "silas": {
        "name": "Silas Bone", "age": 40, "gender": "male",
        "role": "sharpshooter", "special": "sharpshooter",
        "loyalty": 50, "hp": 48,
    },
}


def make_recruit(key):
    """Build a fresh NPC gang member from a template key."""
    data = RECRUITS[key]
    return NPC(
        name=data["name"], age=data["age"], gender=data["gender"],
        role=data["role"], loyalty=data["loyalty"], hp=data["hp"],
        special=data["special"], disposition="loyal",
    )


# Camp upgrades bought with gang funds. effect is applied by the systems that
# read it (combat reads ally_damage_bonus; travel reads camp_heal).
CAMP_UPGRADES = {
    "gunsmith": {
        "name": "Camp Gunsmith",
        "cost": 100,
        "desc": "Better gear — gang backup hits harder (+3 ally damage).",
    },
    "infirmary": {
        "name": "Field Infirmary",
        "cost": 150,
        "desc": "Rest heals the hero +15 HP each time you return to camp.",
    },
    "war_chest": {
        "name": "War Chest",
        "cost": 120,
        "desc": "A cause worth staying for — morale decays slower on the trail.",
    },
}
