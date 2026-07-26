# src/ on path so "python tests/test_combat.py" works from anywhere.
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

"""
End-to-end test for Milestone 4: Combat & Dead Eye Duels.

Runs headless by stubbing the interactive UI (Dialogue.choose + console) the
combat module depends on.
"""
import sys

from iron_rust.core import combat as combat_mod
from iron_rust.core.combat import Combat, start_duel
from iron_rust.entities.enemy import Enemy
from iron_rust.entities.hero import Hero


# ---- headless UI stubs -------------------------------------------------------
class FakeDialogue:
    queue = []

    @staticmethod
    def choose(question, options, labels=None):
        if FakeDialogue.queue:
            return FakeDialogue.queue.pop(0)
        return options[0]        # combat now always prompts; default to a shot


class FakeConsole:
    @staticmethod
    def print(*a, **k):
        pass

    @staticmethod
    def input(prompt=""):
        return ""


combat_mod.Dialogue = FakeDialogue
combat_mod.console = FakeConsole


def fresh_hero():
    return Hero(name="Tester", age=30, gender="male", role="cowboy", archetype="gunslinger")


def check(label, condition):
    print(f"  [{'PASS' if condition else 'FAIL'}] {label}")
    return condition


ok = True

# --- Single-enemy duel -> VICTORY -------------------------------------------
print("Task 9 — single-enemy duel to a WIN")
hero = fresh_hero()
weakling = Enemy("Drifter", hp=5, aim=0, attack=1, threat_level=1)
result = start_duel(hero, weakling)
ok &= check("result is victory", result == "victory")
ok &= check("enemy is dead", weakling.hp == 0)
ok &= check("hero survived", hero.hp > 0)

# --- Single-enemy duel -> DEFEAT --------------------------------------------
print("\nTask 9 — single-enemy duel to a LOSS")
hero = fresh_hero()
hero.hp = 5
juggernaut = Enemy("Executioner", hp=500, aim=30, attack=50, threat_level=5)
result = start_duel(hero, juggernaut)
ok &= check("result is defeat", result == "defeat")
ok &= check("hero is down (hp 0)", hero.hp == 0)
ok &= check("enemy still alive", juggernaut.hp > 0)

# --- Dead Eye ranks by threat_level (heapq) ---------------------------------
print("\nTask 9 — Dead Eye ranks targets by threat_level")
low = Enemy("Bandit", hp=30, aim=5, attack=8, threat_level=2)
high = Enemy("Gunslinger", hp=40, aim=9, attack=14, threat_level=5)
mid = Enemy("Lawman", hp=45, aim=7, attack=11, threat_level=3)
ranked = Combat.rank_targets([low, high, mid])
ok &= check("ranked order is 5,3,2 by threat", [e.threat_level for e in ranked] == [5, 3, 2])

# --- Dead Eye tags top targets, guaranteed hits, resets meter ----------------
print("\nTask 9 — Dead Eye combo tags top-threat targets and fires")
hero = fresh_hero()
hero.deadeye = hero.DEADEYE_MAX                      # meter full -> Dead Eye ready
e2 = Enemy("Bandit", hp=5, aim=5, attack=8, threat_level=2)
e5 = Enemy("Gunslinger", hp=5, aim=9, attack=14, threat_level=5)
e3 = Enemy("Lawman", hp=5, aim=7, attack=11, threat_level=3)
fight = Combat(hero, [e2, e5, e3])
# One hero turn: choose "deadeye", then tag all three (ranked order 0,0,0).
FakeDialogue.queue = ["deadeye", 0, 0, 0]
ok &= check("hero starts Dead Eye ready", hero.deadeye_ready)
fight._hero_turn()
tagged = [e.threat_level for e in fight.last_deadeye_targets]
ok &= check("combo tagged in threat order 5,3,2", tagged == [5, 3, 2])
ok &= check("all three tagged enemies down", e2.hp == 0 and e5.hp == 0 and e3.hp == 0)
ok &= check("Dead Eye meter reset to 0", hero.deadeye == 0)

# --- Full multi-enemy run driven by Dead Eye -> victory ----------------------
print("\nTask 9 — full multi-enemy duel won via Dead Eye")
hero = fresh_hero()
hero.deadeye = hero.DEADEYE_MAX
enemies = [
    Enemy("Bandit", hp=6, aim=0, attack=1, threat_level=2),
    Enemy("Gunslinger", hp=6, aim=0, attack=1, threat_level=5),
    Enemy("Lawman", hp=6, aim=0, attack=1, threat_level=3),
]
fight = Combat(hero, enemies)
FakeDialogue.queue = ["deadeye", 0, 0, 0]
result = fight.run()
ok &= check("multi-enemy result is victory", result == "victory")
ok &= check("Dead Eye targets ranked 5,3,2",
            [e.threat_level for e in fight.last_deadeye_targets] == [5, 3, 2])

print("\n" + ("ALL TESTS PASSED" if ok else "SOME TESTS FAILED"))
sys.exit(0 if ok else 1)
