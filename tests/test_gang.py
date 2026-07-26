# src/ on path so "python tests/test_gang.py" works from anywhere.
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

"""
End-to-end test for Milestone 5: Gang Camp.

Runs headless by stubbing the interactive UI in camp.py, quest.py, and combat.py.
"""
import sys

from iron_rust.core import camp as camp_mod
from iron_rust.core import combat as combat_mod
from iron_rust.core.camp import camp_menu
from iron_rust.core.combat import Combat, start_duel
from iron_rust.entities.enemy import Enemy
from iron_rust.entities.gang import Gang
from iron_rust.entities.hero import Hero
from iron_rust.quests import quest as quest_mod
from iron_rust.quests.side_quests import the_reunion


class FakeDialogue:
    choices = []
    ints = []

    @staticmethod
    def choose(question, options, labels=None):
        if FakeDialogue.choices:
            return FakeDialogue.choices.pop(0)
        return options[0]        # combat now always prompts; default to a shot

    @staticmethod
    def ask_int(question):
        return FakeDialogue.ints.pop(0)

    @staticmethod
    def say(text):
        pass

    @staticmethod
    def narrator(text):
        pass

    @staticmethod
    def success(text):
        pass

    @staticmethod
    def pause(seconds=0):
        pass


class FakeConsole:
    @staticmethod
    def print(*a, **k):
        pass

    @staticmethod
    def input(prompt=""):
        return ""


# Inject stubs everywhere the interactive UI is used.
camp_mod.console = FakeConsole
combat_mod.Dialogue = FakeDialogue
combat_mod.console = FakeConsole
quest_mod.Dialogue = FakeDialogue
quest_mod.console = FakeConsole


def fresh_hero():
    return Hero(name="Tester", age=30, gender="male", role="cowboy", archetype="gunslinger")


def check(label, condition):
    print(f"  [{'PASS' if condition else 'FAIL'}] {label}")
    return condition


ok = True

# --- Task 8a: contribute funds -> morale rises ------------------------------
print("Task 8 — contributing funds raises morale")
hero = fresh_hero()
hero.money = 200
start_morale = hero.gang.morale
start_funds = hero.gang.funds
# camp_menu: choose 'contribute', give $50, then 'leave'.
FakeDialogue.choices = ["contribute", "leave"]
FakeDialogue.ints = [50]
camp_menu(hero, FakeDialogue)
ok &= check("gang funds went up by $50", hero.gang.funds == start_funds + 50)
ok &= check("hero money dropped by $50", hero.money == 150)
ok &= check("morale rose (+$50 / $5 = +10)", hero.gang.morale == start_morale + 10)

# direct method sanity
g = Gang("Test", morale=50)
gained = g.contribute(25)
ok &= check("Gang.contribute($25) -> +5 morale", gained == 5 and g.morale == 55 and g.funds == 25)

# --- Task 8b: recruit via the quest node ------------------------------------
print("\nTask 8 — recruiting Eli through the quest node")
hero = fresh_hero()
ok &= check("gang starts empty", len(hero.gang.members) == 0)
FakeDialogue.choices = [0]     # choose the recruit branch (index 0)
end_id = the_reunion.play(hero)
ok &= check("ended on 'reunion_join'", end_id == "reunion_join")
ok &= check("one member recruited", len(hero.gang.members) == 1)
ok &= check("member is Eli Vance", hero.gang.members[0].name == "Eli Vance")
ok &= check("member has a role + loyalty", hero.gang.members[0].role == "backup gunslinger"
            and hero.gang.members[0].loyalty == 70)

# declining does NOT recruit
hero2 = fresh_hero()
FakeDialogue.choices = [1]     # ride on alone
the_reunion.play(hero2)
ok &= check("declining recruits no one", len(hero2.gang.members) == 0)

# --- Task 8c: morale >= 60 -> backup joins the turn queue -------------------
print("\nTask 8 — with morale >= 60 the gang member enters the turn queue")
hero = fresh_hero()
FakeDialogue.choices = [0]
the_reunion.play(hero)                     # recruit Eli
hero.gang.morale = 65                      # push morale over the threshold
ok &= check("gang reports backup_ready", hero.gang.backup_ready)
backup = hero.gang.best_backup()
ok &= check("best_backup is Eli", backup is not None and backup.name == "Eli Vance")

enemies = [Enemy("Bandit", hp=30, aim=5, attack=8, threat_level=2)]
fight = Combat(hero, enemies, allies=[backup])
order = fight._build_order()
ok &= check("hero is first in the queue", order[0] is hero)
ok &= check("Eli is in the turn queue", backup in order)
ok &= check("queue is hero, ally, enemy", list(order) == [hero, backup, enemies[0]])

# And when morale is too low, no backup is eligible.
hero.gang.morale = 40
ok &= check("morale 40 -> backup not ready", not hero.gang.backup_ready)

# --- prove the ally actually ACTS in a live duel ----------------------------
print("\nTask 8 — the backup actually takes its turn in a duel")
hero = fresh_hero()
hero.stats["aim"] = -99                     # hero always misses, so any kill is the ally's
gunslinger = camp_backup = None
FakeDialogue.choices = [0]
the_reunion.play(hero)
ally = hero.gang.best_backup()
lone_enemy = Enemy("Straggler", hp=8, aim=-99, attack=1, threat_level=1)  # enemy always misses too
result = start_duel(hero, lone_enemy, allies=[ally])
ok &= check("duel resolved to victory via the ally's fire", result == "victory")
ok &= check("enemy was downed (only the ally could do it)", lone_enemy.hp == 0)

print("\n" + ("ALL TESTS PASSED" if ok else "SOME TESTS FAILED"))
sys.exit(0 if ok else 1)
