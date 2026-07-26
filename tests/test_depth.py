# src/ on path so "python tests/test_depth.py" works from anywhere.
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

"""Milestone 7 — Depth Pass. Tests the new stat effects, economy, combat
options, gang stakes, persistence, DSA usage, and gang-aware endings."""
import sys

from iron_rust.core import combat as combat_mod
from iron_rust.core import shop as shop_mod
from iron_rust.core.combat import Combat, start_duel
from iron_rust.core import save_manager
from iron_rust.core.shop import buy_price, sell_price, _buy
from iron_rust.entities.enemy import Enemy
from iron_rust.entities.gang import Gang
from iron_rust.entities.hero import Hero
from iron_rust.entities import gang as gang_mod
from iron_rust.quests import act2, quest as quest_mod
from iron_rust.quests.endings import determine_ending
from iron_rust.quests.side_quests import the_stagecoach, the_field_medic
from iron_rust.data.recruits import make_recruit, CAMP_UPGRADES
from iron_rust.utils.ascii_art import load_art


class FakeDialogue:
    q = []
    fallback = None
    ints = []

    @staticmethod
    def choose(question, options, labels=None):
        if FakeDialogue.q:
            return FakeDialogue.q.pop(0)
        if FakeDialogue.fallback is not None:
            return FakeDialogue.fallback
        return options[0]

    @staticmethod
    def ask_int(question):
        return FakeDialogue.ints.pop(0)

    say = narrator = success = staticmethod(lambda *a, **k: None)
    pause = divider = clear = staticmethod(lambda *a, **k: None)
    panel = staticmethod(lambda *a, **k: None)


class FakeConsole:
    print = staticmethod(lambda *a, **k: None)
    input = staticmethod(lambda *a, **k: "")


combat_mod.Dialogue = FakeDialogue
combat_mod.console = FakeConsole
shop_mod.Dialogue = FakeDialogue
shop_mod.console = FakeConsole
quest_mod.Dialogue = FakeDialogue
quest_mod.console = FakeConsole
act2.Dialogue = FakeDialogue


def fresh_hero():
    return Hero(name="Tester", age=30, gender="male", role="cowboy", archetype="gunslinger")


def check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    return cond


ok = True

# --- A. Stats that do something ---------------------------------------------
print("A. Stats")
h = fresh_hero()
h.stats["intelligence"] = 8
ok &= check("intelligence speeds Dead Eye (30 + 8//4 = 32)", Combat(h, []). _deadeye_gain() == 32)

h = fresh_hero()
h.stats["luck"] = 100
dmg, crit = Combat(h, [])._apply_luck_crit(10)
ok &= check("luck 100 -> guaranteed crit doubles damage", crit and dmg == 20)
h.stats["luck"] = 0
_, crit0 = Combat(h, [])._apply_luck_crit(10)
ok &= check("luck 0 -> no crit", not crit0)

h = fresh_hero()
h.stats["stealth"] = 1000
FakeDialogue.fallback = "flee"
res = start_duel(h, Enemy("Goon", hp=30, aim=5, attack=8, threat_level=2))
FakeDialogue.fallback = None
ok &= check("high stealth flee succeeds -> 'fled'", res == "fled")

# --- Items & combat item turn (Task 12) -------------------------------------
print("\nItems")
h = fresh_hero()
h.hp = 40
h.consumables = {"medkit": 1}
c = Combat(h, [Enemy("x", 10, 5, 5, 1)])
c._use_item_turn()
ok &= check("medkit used in combat heals +50", h.hp == 90 and "medkit" not in h.consumables)
h.consumables = {"tonic": 1}
h.deadeye = 0
Combat(h, [])._use_item_turn() if False else h.use_item("tonic")
ok &= check("tonic adds Dead Eye", h.deadeye == 50)

# --- Ally specials (Task 15) ------------------------------------------------
print("\nAlly specials")
h = fresh_hero()
enemies = [Enemy("a", 6, 5, 5, 2), Enemy("b", 6, 5, 5, 5), Enemy("c", 6, 5, 5, 3)]
c = Combat(h, enemies, allies=[make_recruit("kate")])   # dynamite
c._ally_dynamite(c.allies[0])
ok &= check("dynamite hits every enemy", all(e.hp < 6 for e in enemies))

h = fresh_hero()
strong = Enemy("boss", 100, 5, 5, 9)
c = Combat(h, [strong], allies=[make_recruit("silas")])  # sharpshooter
c._ally_sharpshot(c.allies[0])
ok &= check("sharpshooter deals guaranteed high damage", strong.hp <= 86)

h = fresh_hero(); h.hp = 50
c = Combat(h, [Enemy("x", 10, 5, 5, 1)], allies=[make_recruit("doc")])  # medic
c._ally_heal(c.allies[0])
ok &= check("medic heals the hero", h.hp > 50)

h = fresh_hero()
h.gang.upgrades = {"gunsmith"}
ok &= check("gunsmith upgrade grants ally damage bonus", Combat(h, [])._ally_bonus() == 3)

# --- B. Shop economy (Tasks 5, 6, 20) ---------------------------------------
print("\nShop economy")
h = fresh_hero()
h.stats["charisma"] = 10
ok &= check("charisma 10 -> 20% off buying ($100 -> $80)", buy_price(h, 100) == 80)
ok &= check("charisma 10 -> better sell ($100 -> $60)", sell_price(h, 100) == 60)
h.stats["charisma"] = 0
ok &= check("charisma 0 -> full buy price", buy_price(h, 100) == 100)

h = fresh_hero(); h.money = 500; h.stats["charisma"] = 0
shop = {"name": "Test", "weapons": ["revolver"], "items": ["bandage"]}
FakeDialogue.q = ["weapon:revolver"]
_buy(h, shop, FakeDialogue)
ok &= check("buying a weapon equips it and costs money",
            h.equipped_weapon_key == "revolver" and h.money == 500 - 120)

# --- E. Gang stakes (Tasks 16, 17) ------------------------------------------
print("\nGang stakes")
g = Gang("Test", funds=100)
ok &= check("buy affordable upgrade", g.buy_upgrade("gunsmith", CAMP_UPGRADES["gunsmith"]["cost"]) and g.funds == 0)
ok &= check("can't rebuy / can't afford", not g.buy_upgrade("infirmary", 150))

g = Gang("Test", morale=10)
g.add_member(make_recruit("eli"))     # loyalty 70
g.add_member(make_recruit("kate"))    # loyalty 45 (least loyal -> first to walk)
real_random = gang_mod.random
gang_mod.random = type("R", (), {"random": staticmethod(lambda: 0.0)})
deserter = g.check_desertion()
gang_mod.random = real_random
ok &= check("low morale -> least-loyal member deserts", deserter is not None and deserter.role == "demolitionist")
ok &= check("deserter removed from roster", len(g.members) == 1)
g.morale = 80
ok &= check("healthy morale -> nobody deserts", g.check_desertion() is None)

# --- F. Persistence round-trip (Task 18) ------------------------------------
print("\nPersistence")
h = fresh_hero()
h.money = 777; h.honor = 42; h.wanted = 13
h.equip_weapon("rifle")
h.add_item("medkit", 3)
h.gang.add_member(make_recruit("doc"))
h.gang.funds = 200; h.gang.morale = 88; h.gang.upgrades = {"gunsmith"}
h.visited_towns = {"dust_creek", "blackridge"}
h.town_history = ["dust_creek"]
h.story_flags = {"kane_warned"}
h.act3_done = True
save_manager.save_game(h)
loaded = save_manager.load_game()
ok &= check("money/honor/wanted persist", loaded.money == 777 and loaded.honor == 42 and loaded.wanted == 13)
ok &= check("weapon persists", loaded.equipped_weapon_key == "rifle")
ok &= check("consumables persist", loaded.consumables.get("medkit") == 3)
ok &= check("gang persists (member/funds/morale/upgrades)",
            len(loaded.gang.members) == 1 and loaded.gang.members[0].special == "field_medic"
            and loaded.gang.funds == 200 and loaded.gang.morale == 88 and "gunsmith" in loaded.gang.upgrades)
ok &= check("sets/stack/flags persist",
            loaded.visited_towns == {"dust_creek", "blackridge"} and loaded.town_history == ["dust_creek"]
            and "kane_warned" in loaded.story_flags and loaded.act3_done)
save_manager.delete_save()

# --- G. DSA: Set + Stack (Tasks 19, 21) -------------------------------------
print("\nDSA")
h = fresh_hero()
ok &= check("visited_towns is a Set", isinstance(h.visited_towns, set))
h.visited_towns.add("dust_creek")  # dupe of start
ok &= check("Set dedupes visited towns", h.visited_towns == {"dust_creek"})
h.town_history.append("dust_creek"); h.town_history.append("blackridge")
ok &= check("town_history is a LIFO Stack", h.town_history.pop() == "blackridge")

# --- H. Endings factor gang (Task 22) ---------------------------------------
print("\nEndings with gang state")
def hero_with(honor, wanted, morale, members=0, deserters=0):
    h = fresh_hero()
    h.honor, h.wanted = honor, wanted
    h.gang.morale = morale
    h.gang_deserters = deserters
    for _ in range(members):
        h.gang.add_member(make_recruit("eli"))
    return h

ok &= check("outlaw_king needs a loyal gang (has one)", determine_ending(hero_with(80, 80, 70, members=1)) == "outlaw_king")
ok &= check("no gang -> outlaw_king downgrades to legend", determine_ending(hero_with(80, 80, 70, members=0)) == "legend")
ok &= check("deserters disqualify outlaw_king", determine_ending(hero_with(80, 80, 70, members=1, deserters=1)) == "legend")
ok &= check("loyal gang, quiet hero -> gang_leader", determine_ending(hero_with(0, 0, 70, members=1)) == "gang_leader")
ok &= check("no gang, quiet hero -> drifter", determine_ending(hero_with(0, 0, 50, members=0)) == "drifter")

# --- C. Act 2 arcs (Tasks 8, 9) ---------------------------------------------
print("\nAct 2 arcs")
h = fresh_hero(); h.location = "silver_crossing"; h.wanted = 5
act2.maybe_lawman(h, FakeDialogue)
ok &= check("lawman: low wanted -> peaceful, flag set", "kane_seen_silver_crossing" in h.story_flags and h.wanted == 5)

h = fresh_hero(); h.location = "iron_forge"; h.wanted = 70
act2.start_duel = lambda hero, enemies, allies=None: "victory"
act2.maybe_lawman(h, FakeDialogue)
ok &= check("lawman: high wanted -> duel, wanted drops on win", h.wanted == 45 and "kane_beaten" in h.story_flags)

h = fresh_hero(); h.location = "redemption"; h.honor = -20
FakeDialogue.q = ["accept"]
act2.maybe_preacher(h, FakeDialogue)
ok &= check("preacher: low honor accept -> +15 honor", h.honor == -5 and "preacher_done" in h.story_flags)

# --- D. Side quests reward (Task 10) ----------------------------------------
print("\nSide quests")
h = fresh_hero(); money0 = h.money
FakeDialogue.q = [0]     # stagecoach: help
the_stagecoach.play(h)
ok &= check("stagecoach help -> +$80, +honor", h.money == money0 + 80 and h.honor == 10)

h = fresh_hero(); h.money = 100
FakeDialogue.q = [0]     # field medic: pay debt, recruit Doc
the_field_medic.play(h)
ok &= check("field medic recruit -> Doc joins, -$40", h.money == 60
            and any(m.special == "field_medic" for m in h.gang.members))

# --- Assets (Task 7) --------------------------------------------------------
print("\nAssets")
ok &= check("ASCII art loads for a town", "DUST CREEK" in load_art("dust_creek"))

print("\n" + ("ALL TESTS PASSED" if ok else "SOME TESTS FAILED"))
sys.exit(0 if ok else 1)
