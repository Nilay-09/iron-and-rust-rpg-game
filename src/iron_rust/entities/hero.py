from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from iron_rust.data.archetypes import ARCHETYPES
from iron_rust.data.items import ITEMS
from iron_rust.data.roles import ROLES
from iron_rust.data.towns import STARTING_TOWN
from iron_rust.data.weapons import DEFAULT_WEAPON, WEAPONS
from iron_rust.entities.gang import Gang
from .person import Person

console = Console()


class Hero(Person):
    """
    The player character and the anchor for all game state.

    Beyond the basics (stats, hp, money, inventory) the Hero carries the
    reputation that drives the story — honor and wanted, per-faction and per-NPC
    standing, world-memory flags — plus the gang, the Dead Eye meter, companion
    bonuses, the quest journal, and any active pursuer. Almost everything the
    world remembers lives here, which is what the save file serializes.
    """

    # Reputation bounds.
    HONOR_MIN, HONOR_MAX = -100, 100     # saint <-> outlaw
    WANTED_MIN, WANTED_MAX = 0, 100       # unknown <-> most-wanted

    MAX_HP = 100

    # Dead Eye meter fills to this, then can be triggered.
    DEADEYE_MAX = 100

    def __init__(self, name, age, gender, role, archetype, location: str | None = None):
        super().__init__(name, age, gender, role)

        self.archetype = archetype
        self.stats = ARCHETYPES[archetype].copy()
        self.hp = 100

        self.location = location if location is not None else STARTING_TOWN

        self.honor = 0
        self.wanted = 0
        self.money = ROLES[self.role]["starting_money"]
        self.inventory = ROLES[self.role]["starting_items"]

        self.equipped_weapon = WEAPONS[DEFAULT_WEAPON]
        self.equipped_weapon_key = DEFAULT_WEAPON
        self.deadeye = 0

        # Usable items {item_key: count}. Kept apart from the flavor inventory.
        self.consumables = {"bandage": 1}

        self.gang = Gang(name=f"{self.name}'s Gang")

        # Act 3 unlock tracking.
        self.visited_towns = {self.location}          # DSA: Set (Task 19)
        self.town_history = []                        # DSA: Stack (Task 21)
        self.act3_done = False

        # Optional story encounters already triggered (so they fire once).
        self.seen_encounters = set()                  # DSA: Set (Task 19)

        # Story/quest flags and gang-loss tracking (for save + endings).
        self.story_flags = set()
        self.gang_deserters = 0

        # -- Milestone 8: the world remembers --------------------------------
        self.flags = {}                              # named world memory (Task 1)
        self.factions = {"law": 0, "gang": 0}        # global faction rep (Task 4)
        self.town_rep = {}                           # per-town townsfolk rep (Task 4/9)
        self.relationships = {}                      # per-NPC relationship (Task 3)
        self.statuses = []                           # combat status effects (Task 8)
        self.journal = {}                            # quest journal (Task 11)
        self.companion_bonuses = set()               # companion-arc rewards (Task 10)
        self.pursuer = None                          # active pursuer state (Task 5)

    @property
    def alive(self):
        return self.hp > 0

    # -- stats ----------------------------------------------------------------

    def stat(self, name):
        """Convenience accessor for a numeric stat (0 if absent)."""
        value = self.stats.get(name, 0)
        return value if isinstance(value, (int, float)) else 0

    # -- world memory: flags, factions, relationships (Tasks 1, 3, 4) ---------

    def set_flag(self, name, value=True):
        self.flags[name] = value

    def has_flag(self, name):
        return bool(self.flags.get(name))

    def faction(self, name):
        return self.factions.get(name, 0)

    def adjust_faction(self, name, amount):
        self.factions[name] = self.factions.get(name, 0) + amount
        return self.factions[name]

    def relationship(self, npc):
        return self.relationships.get(npc, 0)

    def adjust_relationship(self, npc, amount):
        self.relationships[npc] = self.relationships.get(npc, 0) + amount
        return self.relationships[npc]

    def town_reputation(self, town):
        return self.town_rep.get(town, 0)

    def adjust_town_rep(self, town, amount):
        self.town_rep[town] = self.town_rep.get(town, 0) + amount
        return self.town_rep[town]

    # -- companion-arc bonuses (Task 10) --------------------------------------

    def has_bonus(self, key):
        return key in self.companion_bonuses

    def grant_bonus(self, key):
        self.companion_bonuses.add(key)

    # -- quest journal (Task 11) ----------------------------------------------

    def journal_add(self, qid, title, status="active", note=""):
        self.journal[qid] = {"title": title, "status": status, "note": note}

    def journal_update(self, qid, status=None, note=None):
        entry = self.journal.get(qid)
        if entry is None:
            return
        if status is not None:
            entry["status"] = status
        if note is not None:
            entry["note"] = note

    # -- health & items -------------------------------------------------------

    def heal(self, amount):
        """Restore HP, capped at MAX_HP. Returns HP actually healed."""
        before = self.hp
        self.hp = min(self.MAX_HP, self.hp + amount)
        return self.hp - before

    def add_item(self, key, qty=1):
        self.consumables[key] = self.consumables.get(key, 0) + qty

    def has_items(self):
        return any(count > 0 for count in self.consumables.values())

    def use_item(self, key):
        """
        Apply a consumable's effect and decrement it. Returns a short result
        string, or None if the item isn't held.
        """
        if self.consumables.get(key, 0) <= 0:
            return None
        item = ITEMS[key]
        self.consumables[key] -= 1
        if self.consumables[key] <= 0:
            del self.consumables[key]

        if item["type"] == "heal":
            healed = self.heal(item["heal"])
            return f"{item['name']}: +{healed} HP."
        if item["type"] == "deadeye":
            self.gain_deadeye(item["deadeye"])
            return f"{item['name']}: +{item['deadeye']} Dead Eye."
        return f"{item['name']} used."

    def equip_weapon(self, key):
        self.equipped_weapon = WEAPONS[key]
        self.equipped_weapon_key = key

    def gain_deadeye(self, amount):
        """Fill the Dead Eye meter, capped at DEADEYE_MAX. Returns new value."""
        self.deadeye = max(0, min(self.DEADEYE_MAX, self.deadeye + amount))
        return self.deadeye

    @property
    def deadeye_ready(self):
        return self.deadeye >= self.DEADEYE_MAX

    def adjust_honor(self, amount):
        """Shift honor by amount, clamped to [HONOR_MIN, HONOR_MAX]. Returns new honor."""
        self.honor = max(self.HONOR_MIN, min(self.HONOR_MAX, self.honor + amount))
        return self.honor

    def adjust_wanted(self, amount):
        """Shift the wanted level by amount, clamped to [WANTED_MIN, WANTED_MAX]. Returns new value."""
        self.wanted = max(self.WANTED_MIN, min(self.WANTED_MAX, self.wanted + amount))
        return self.wanted

    def show_sheet(self):
        stats_text = "\n".join(f"{name}: {value}" for name, value in self.stats.items())
        inventory_text = ", ".join(self.inventory) if isinstance(self.inventory, list) else str(self.inventory)

        table = Table.grid(padding=(0, 2))
        table.add_column(justify="right", style="bold cyan")
        table.add_column()
        table.add_row("Name", self.name)
        table.add_row("Age", str(self.age))
        table.add_row("Gender", self.gender)
        table.add_row("Role", self.role)
        table.add_row("Location", self.location)
        table.add_row("Archetype", self.archetype)
        table.add_row("HP", str(self.hp))
        table.add_row("Weapon", self.equipped_weapon["name"])
        table.add_row("Stats", stats_text)
        table.add_row("Honor", str(self.honor))
        table.add_row("Wanted", str(self.wanted))
        table.add_row("Money", f"${self.money}")
        table.add_row("Inventory", inventory_text)

        panel = Panel(table, title="CHARACTER SHEET", border_style="green", padding=(1, 2))
        console.print(panel)
