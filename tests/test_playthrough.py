# src/ on path so "python tests/test_playthrough.py" works from anywhere.
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

"""
Milestone 9 / Task 2 — integration playthrough.

A headless proxy for "play it start to finish 4 times." Part 1 runs many real
journeys to shake out crashes in the transitions between systems (trail events,
side quests, ambush combat with statuses/called shots, camp, Act 2 NPCs, active
pursuit). Part 2 drives all four ending branches through play_act3.
"""
import io
import random
import sys

from rich.console import Console

from iron_rust.core import combat as combat_mod
from iron_rust.core import camp as camp_mod
from iron_rust.core import shop as shop_mod
from iron_rust.core import save_manager
from iron_rust.quests import act2, quest as quest_mod, main_story
from iron_rust.quests.main_story import play_act3, the_fall
from iron_rust.data.recruits import make_recruit
from iron_rust.entities.hero import Hero
from iron_rust.world import travel as travel_mod
from iron_rust.world.travel import _travel_to
from iron_rust.world.routes import world

QUIET = Console(file=io.StringIO(), width=80)


class FakeDialogue:
    q = []

    @staticmethod
    def choose(question, options, labels=None):
        return FakeDialogue.q.pop(0) if FakeDialogue.q else options[0]

    say = narrator = success = staticmethod(lambda *a, **k: None)
    pause = divider = clear = press_enter = staticmethod(lambda *a, **k: None)
    panel = staticmethod(lambda *a, **k: None)
    ask = staticmethod(lambda *a, **k: "")
    ask_int = staticmethod(lambda *a, **k: 0)


# Silence output and kill the animation delays across every module in the loop.
for mod in (travel_mod, combat_mod, camp_mod, shop_mod, quest_mod, main_story):
    if hasattr(mod, "console"):
        mod.console = QUIET
    if hasattr(mod, "Dialogue"):
        mod.Dialogue = FakeDialogue
act2.Dialogue = FakeDialogue
travel_mod.sleep = lambda *a, **k: None


def build_hero():
    return Hero(name="Tester", age=30, gender="male", role="cowboy", archetype="gunslinger")


def check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    return cond


ok = True

# --- Part 1: a long, real journey loop — does anything crash? ---------------
print("Part 1 — 16-leg journey stressing every system together")
random.seed(7)
crashed = None
try:
    hero = build_hero()
    the_fall.play(hero)
    for i in range(16):
        neighbors = list(world.neighbors(hero.location))
        dest = random.choice(neighbors)
        if i == 8:
            hero.wanted = 60          # trip the active pursuit mid-run
        _travel_to(hero, world, FakeDialogue, hero.location, dest)
except Exception as e:               # noqa: BLE001 — we want to catch anything
    import traceback
    crashed = traceback.format_exc()

ok &= check("16 journeys completed without an exception", crashed is None)
if crashed:
    print(crashed)
else:
    ok &= check("hero is still in a valid town", hero.location in world.towns())
    ok &= check("hp stayed within bounds", 0 <= hero.hp <= hero.MAX_HP)

# --- Part 2: every ending branch, start to finish ---------------------------
print("\nPart 2 — steering to each ending through play_act3")
main_story.start_duel = lambda hero, enemies, allies=None: "victory"   # survive the boss


def make_for(honor, wanted, morale=50, members=0, deserters=0):
    h = build_hero()
    the_fall.play(h)
    h.honor, h.wanted = honor, wanted
    h.gang.morale = morale
    h.gang_deserters = deserters
    for _ in range(members):
        h.gang.add_member(make_recruit("eli"))
    return h


# Note: the final verdict defaults to "kill" (honor -10, wanted +10) via FakeDialogue.
scenarios = [
    ("Redemption",   make_for(95, 5),               "redemption"),
    ("Legend",       make_for(10, 70),              "legend"),
    ("Hunted Down",  make_for(-60, 80),             "hunted_down"),
    ("Outlaw King",  make_for(80, 80, 70, members=1), "outlaw_king"),
]
for name, hero, expected in scenarios:
    got = play_act3(hero)
    ok &= check(f"{name:<12} playthrough -> {expected}", got == expected)

# --- Part 3: a lost boss duel still ends the story (died_boots) -------------
print("\nPart 3 — losing the final duel ends cleanly")
main_story.start_duel = lambda hero, enemies, allies=None: "defeat"
got = play_act3(make_for(95, 5))
ok &= check("boss defeat -> died_boots", got == "died_boots")

save_manager.delete_save()   # clean up any autosaves written during the loop

print("\n" + ("ALL TESTS PASSED" if ok else "SOME TESTS FAILED"))
sys.exit(0 if ok else 1)
