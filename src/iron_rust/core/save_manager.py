"""
Persistence — serialize the hero, gang, story flags, and world position to JSON
and load them back on startup so progress survives between runs (Task 18).
"""

import json
import os
import sys
from pathlib import Path

from iron_rust.entities.hero import Hero
from iron_rust.entities.npc import NPC

APP_NAME = "IronAndRust"


def _save_dir():
    """Per-user save location, kept out of the installed package (Step 8)."""
    if sys.platform.startswith("win"):
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser(r"~\AppData\Local")
        return Path(base) / APP_NAME / "saves"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME / "saves"
    # Linux / other Unix — follow the XDG base-directory spec.
    base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    return Path(base) / "iron-and-rust" / "saves"


SAVE_DIR = _save_dir()
SAVE_PATH = SAVE_DIR / "save1.json"


# -- serialize ---------------------------------------------------------------

def _member_to_dict(m):
    return {
        "name": m.name, "age": m.age, "gender": m.gender, "role": m.role,
        "disposition": getattr(m, "disposition", "loyal"),
        "loyalty": getattr(m, "loyalty", 50),
        "hp": getattr(m, "hp", 50),
        "special": getattr(m, "special", None),
    }


def _gang_to_dict(gang):
    return {
        "name": gang.name,
        "funds": gang.funds,
        "morale": gang.morale,
        "upgrades": sorted(gang.upgrades),
        "members": [_member_to_dict(m) for m in gang.members],
    }


def hero_to_dict(hero):
    return {
        "name": hero.name, "age": hero.age, "gender": hero.gender,
        "role": hero.role, "archetype": hero.archetype,
        "hp": hero.hp, "location": hero.location,
        "honor": hero.honor, "wanted": hero.wanted, "money": hero.money,
        "deadeye": hero.deadeye,
        "equipped_weapon": hero.equipped_weapon_key,
        "consumables": dict(hero.consumables),
        "inventory": list(hero.inventory) if isinstance(hero.inventory, list) else hero.inventory,
        "visited_towns": sorted(hero.visited_towns),      # Set -> list
        "town_history": list(hero.town_history),          # Stack -> list
        "seen_encounters": sorted(hero.seen_encounters),
        "story_flags": sorted(hero.story_flags),
        "act3_done": hero.act3_done,
        "gang_deserters": hero.gang_deserters,
        "gang": _gang_to_dict(hero.gang),
        # Milestone 8: world memory.
        "flags": dict(hero.flags),
        "factions": dict(hero.factions),
        "town_rep": dict(hero.town_rep),
        "relationships": dict(hero.relationships),
        "journal": dict(hero.journal),
        "companion_bonuses": sorted(hero.companion_bonuses),
        "pursuer": hero.pursuer,
    }


# -- deserialize -------------------------------------------------------------

def _member_from_dict(d):
    return NPC(
        name=d["name"], age=d["age"], gender=d["gender"], role=d["role"],
        disposition=d.get("disposition", "loyal"),
        loyalty=d.get("loyalty", 50), hp=d.get("hp", 50),
        special=d.get("special"),
    )


def hero_from_dict(data):
    hero = Hero(
        name=data["name"], age=data["age"], gender=data["gender"],
        role=data["role"], archetype=data["archetype"],
        location=data["location"],
    )
    hero.hp = data["hp"]
    hero.honor = data["honor"]
    hero.wanted = data["wanted"]
    hero.money = data["money"]
    hero.deadeye = data.get("deadeye", 0)
    hero.equip_weapon(data.get("equipped_weapon", hero.equipped_weapon_key))
    hero.consumables = dict(data.get("consumables", {}))
    hero.inventory = data.get("inventory", hero.inventory)
    hero.visited_towns = set(data.get("visited_towns", [hero.location]))
    hero.town_history = list(data.get("town_history", []))
    hero.seen_encounters = set(data.get("seen_encounters", []))
    hero.story_flags = set(data.get("story_flags", []))
    hero.act3_done = data.get("act3_done", False)
    hero.gang_deserters = data.get("gang_deserters", 0)

    # Milestone 8: world memory.
    hero.flags = dict(data.get("flags", {}))
    hero.factions = dict(data.get("factions", {"law": 0, "gang": 0}))
    hero.town_rep = dict(data.get("town_rep", {}))
    hero.relationships = dict(data.get("relationships", {}))
    hero.journal = dict(data.get("journal", {}))
    hero.companion_bonuses = set(data.get("companion_bonuses", []))
    hero.pursuer = data.get("pursuer")

    g = hero.gang
    gd = data.get("gang", {})
    g.name = gd.get("name", g.name)
    g.funds = gd.get("funds", 0)
    g.morale = gd.get("morale", 50)
    g.upgrades = set(gd.get("upgrades", []))
    g.members = [_member_from_dict(m) for m in gd.get("members", [])]
    return hero


# -- disk --------------------------------------------------------------------

def save_game(hero):
    """Write the save. A disk/permission error must never crash a playthrough."""
    try:
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        with open(SAVE_PATH, "w", encoding="utf-8") as fp:
            json.dump(hero_to_dict(hero), fp, indent=2)
        return True
    except OSError:
        return False


def load_game():
    """Return a reconstructed Hero, or None if there's no save."""
    if not SAVE_PATH.exists():
        return None
    with open(SAVE_PATH, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    if not data:
        return None
    return hero_from_dict(data)


def has_save():
    return SAVE_PATH.exists()


def delete_save():
    if SAVE_PATH.exists():
        SAVE_PATH.unlink()
