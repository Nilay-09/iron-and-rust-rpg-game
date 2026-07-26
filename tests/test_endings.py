# src/ on path so "python tests/test_endings.py" works from anywhere.
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

"""
End-to-end test for Milestone 6: Endings (Act 3 — Reckoning).

Checks determine_ending across every branch, then drives play_act3 with forced
combat outcomes to confirm the matching epilogue actually plays.
"""
import sys

from iron_rust.data.dialogues import DIALOGUES
from iron_rust.entities.hero import Hero
from iron_rust.quests import main_story
from iron_rust.quests import quest as quest_mod
from iron_rust.quests.endings import determine_ending


class FakeDialogue:
    said = []
    choose_queue = []           # forced choices; falls back to options[0]

    @staticmethod
    def say(text):
        FakeDialogue.said.append(text)

    @staticmethod
    def choose(question, options, labels=None):
        if FakeDialogue.choose_queue:
            return FakeDialogue.choose_queue.pop(0)
        return options[0]

    @staticmethod
    def pause(seconds=0):
        pass

    @staticmethod
    def press_enter(prompt=""):
        pass

    @staticmethod
    def divider():
        pass

    @staticmethod
    def panel(title, text):
        pass

    @staticmethod
    def narrator(text):
        pass

    @staticmethod
    def success(text):
        pass


class FakeConsole:
    @staticmethod
    def print(*a, **k):
        pass

    @staticmethod
    def input(prompt=""):
        return ""


quest_mod.Dialogue = FakeDialogue
quest_mod.console = FakeConsole
main_story.Dialogue = FakeDialogue


from iron_rust.data.recruits import make_recruit


def fresh_hero(honor=0, wanted=0, morale=50, members=0):
    h = Hero(name="Tester", age=30, gender="male", role="cowboy", archetype="gunslinger")
    h.honor = honor
    h.wanted = wanted
    h.gang.morale = morale
    for _ in range(members):        # Task 22: outlaw_king now needs a loyal gang
        h.gang.add_member(make_recruit("eli"))
    return h


def check(label, condition):
    print(f"  [{'PASS' if condition else 'FAIL'}] {label}")
    return condition


ok = True

# --- Task 1: determine_ending covers every branch ---------------------------
print("Task 1/7 — determine_ending picks the right ending")
cases = [
    ("high honor, clean",        90, 10, 50, 0, "redemption"),
    ("notorious, mixed honor",   10, 70, 50, 0, "legend"),
    ("villain, hunted",         -60, 80, 50, 0, "hunted_down"),
    ("beloved + hunted + gang",  80, 80, 70, 1, "outlaw_king"),
    ("beloved + hunted, no gang",80, 80, 70, 0, "legend"),     # no gang gates the secret
    ("did nothing extreme",       0,  0, 50, 0, "drifter"),
]
for name, honor, wanted, morale, members, expected in cases:
    got = determine_ending(fresh_hero(honor, wanted, morale, members))
    ok &= check(f"{name:<28} -> {expected}", got == expected)

# --- Task 6/7: play_act3 defeat is its own ending ---------------------------
print("\nTask 6/7 — losing the final duel gives the 'died_boots' ending")
main_story.start_duel = lambda hero, enemies, allies=None: "defeat"
FakeDialogue.said = []
hero = fresh_hero(honor=90, wanted=10)     # would be redemption on a win...
ending = main_story.play_act3(hero)
ok &= check("defeat -> died_boots regardless of stats", ending == "died_boots")
ok &= check("died_boots epilogue was narrated",
            DIALOGUES["endings"]["died_boots"] in FakeDialogue.said)

# --- Task 3/7: play_act3 victory plays the earned epilogue -------------------
# (choose_queue empty -> the final verdict defaults to "kill": honor-10, wanted+10.)
print("\nTask 3/7 — winning plays the ending the hero earned")
main_story.start_duel = lambda hero, enemies, allies=None: "victory"

for honor, wanted, morale, members, expected in [
    (90, 10, 50, 0, "redemption"),
    (10, 70, 50, 0, "legend"),
    (-60, 80, 50, 0, "hunted_down"),
    (80, 80, 70, 1, "outlaw_king"),      # needs a loyal gang (Task 22)
    (0, 0, 50, 0, "drifter"),
]:
    FakeDialogue.said = []
    FakeDialogue.choose_queue = []          # verdict = kill
    hero = fresh_hero(honor, wanted, morale, members)
    ending = main_story.play_act3(hero)
    good = (ending == expected
            and DIALOGUES["endings"][expected] in FakeDialogue.said)
    ok &= check(f"honor={honor:>4} wanted={wanted:>3} morale={morale:>3} -> {expected}", good)

# --- Part A: the final verdict can flip the ending --------------------------
print("\nPart A — the final moral choice tips the ending")
# Same hero (honor 40, wanted 45). Sparing raises honor / lowers wanted;
# killing lowers honor / raises wanted — landing on different endings.
FakeDialogue.said = []
FakeDialogue.choose_queue = [1]             # verdict_1 choice index 1 = hand to the law
hero = fresh_hero(honor=40, wanted=45, morale=50)
ending = main_story.play_act3(hero)         # -> honor 55, wanted 35
ok &= check("spare (law) -> redemption", ending == "redemption")

FakeDialogue.said = []
FakeDialogue.choose_queue = [0]             # verdict_1 choice index 0 = kill
hero = fresh_hero(honor=40, wanted=45, morale=50)
ending = main_story.play_act3(hero)         # -> honor 30, wanted 55
ok &= check("kill -> legend (same starting stats, different ending)", ending == "legend")

# --- Part B: optional quests wire into travel and fire once -----------------
print("\nPart B — optional encounters surface in travel and move honor/gang")
import iron_rust.world.travel as travel
from iron_rust.quests.main_story import the_crossroads

travel.ENCOUNTER_CHANCE = 1.0                        # force it to fire
travel.OPTIONAL_ENCOUNTERS = [("crossroads", the_crossroads)]

hero = fresh_hero(honor=0, wanted=0, morale=50)
FakeDialogue.choose_queue = [0]                      # crossroads choice 0 = help (+10 honor)
travel._maybe_story_encounter(hero, FakeDialogue)
ok &= check("crossroads fired and raised honor +10", hero.honor == 10)
ok &= check("encounter marked seen", "crossroads" in hero.seen_encounters)

honor_before = hero.honor
FakeDialogue.choose_queue = [0]
travel._maybe_story_encounter(hero, FakeDialogue)   # already seen -> nothing
ok &= check("seen encounter does not fire again", hero.honor == honor_before)

# --- Loophole fix: fleeing the final duel must NOT hand you an ending --------
print("\nLoophole — fleeing the boss postpones the reckoning (no free win)")
main_story.start_duel = lambda hero, enemies, allies=None: "fled"
FakeDialogue.said = []
hero = fresh_hero(95, 5)
result = main_story.play_act3(hero)
ok &= check("fleeing the boss returns None (no ending)", result is None)
ok &= check("no epilogue is narrated when you flee",
            not any(e in FakeDialogue.said for e in DIALOGUES["endings"].values()))

print("\n" + ("ALL TESTS PASSED" if ok else "SOME TESTS FAILED"))
sys.exit(0 if ok else 1)
