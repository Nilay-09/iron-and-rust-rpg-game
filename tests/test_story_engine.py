# src/ on path so "python tests/test_story_engine.py" works from anywhere.
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

"""
End-to-end test for Milestone 3: Story Engine + Honor System.

Runs headless by stubbing the interactive UI (Dialogue.say/choose/pause and
console.input) that quest.py depends on, so play() can be driven by code.
"""
import sys, types

from iron_rust.entities.hero import Hero
from iron_rust.quests import quest as quest_mod
from iron_rust.quests import main_story


# ---- headless UI stubs -------------------------------------------------------
class FakeDialogue:
    picks = []          # queue of choice indices for multi-choice nodes
    said = []           # captured narration

    @staticmethod
    def say(text):
        FakeDialogue.said.append(text)

    @staticmethod
    def pause(seconds=0):
        pass

    @staticmethod
    def press_enter(prompt=""):
        pass

    @staticmethod
    def choose(question, options, labels=None):
        return FakeDialogue.picks.pop(0)


class FakeConsole:
    @staticmethod
    def print(*a, **k):
        pass

    @staticmethod
    def input(prompt=""):
        return ""   # every "press Enter to continue"


# Inject stubs into the quest module.
quest_mod.Dialogue = FakeDialogue
quest_mod.console = FakeConsole


def fresh_hero():
    return Hero(name="Tester", age=30, gender="male", role="cowboy", archetype="gunslinger")


def check(label, condition):
    print(f"  [{'PASS' if condition else 'FAIL'}] {label}")
    return condition


ok = True

# --- Task 1: clamping -------------------------------------------------------
print("Task 1 — adjust_honor / adjust_wanted clamping")
h = fresh_hero()
h.adjust_honor(500)
ok &= check("honor clamps at +100", h.honor == 100)
h.adjust_honor(-500)
ok &= check("honor clamps at -100", h.honor == -100)
h.adjust_wanted(-50)
ok &= check("wanted clamps at 0 (floor)", h.wanted == 0)
h.adjust_wanted(999)
ok &= check("wanted clamps at 100", h.wanted == 100)
h2 = fresh_hero()
h2.adjust_honor(25)
h2.adjust_honor(-10)
ok &= check("honor accumulates (25-10=15)", h2.honor == 15)

# --- Task 7a: The Fall plays linearly, honor untouched ----------------------
print("\nTask 7 — Act 1 'The Fall' plays out with honor/wanted untouched")
h = fresh_hero()
FakeDialogue.said = []
end_id = main_story.the_fall.play(h)
ok &= check("all 5 nodes narrated", len(FakeDialogue.said) == 5)
ok &= check("ended on terminal node 'fall_end'", end_id == "fall_end")
ok &= check("honor still 0 after The Fall", h.honor == 0)
ok &= check("wanted still 0 after The Fall", h.wanted == 0)

# --- Task 7b: branch RIGHT (help) raises honor ------------------------------
print("\nTask 7 — Branching node, HELP choice (index 0)")
h = fresh_hero()
FakeDialogue.picks = [0]
end_id = main_story.the_crossroads.play(h)
ok &= check("ended on 'cross_help'", end_id == "cross_help")
ok &= check("honor rose to +10", h.honor == 10)
ok &= check("wanted unchanged (0)", h.wanted == 0)

# --- Task 7c: branch LEFT (rob) lowers honor, raises wanted -----------------
print("\nTask 7 — Branching node, ROB choice (index 1)")
h = fresh_hero()
FakeDialogue.picks = [1]
end_id = main_story.the_crossroads.play(h)
ok &= check("ended on 'cross_rob'", end_id == "cross_rob")
ok &= check("honor fell to -10", h.honor == -10)
ok &= check("wanted rose to +5", h.wanted == 5)

print("\n" + ("ALL TESTS PASSED" if ok else "SOME TESTS FAILED"))
sys.exit(0 if ok else 1)
