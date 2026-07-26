# src/ on path so "python tests/test_memory.py" works from anywhere.
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

"""Milestone 8 — Systemic Depth. Tests flags, factions/relationships, active
Dijkstra pursuit, called shots + status effects, dynamic economy, companion
arcs, and the quest journal."""
import sys

from iron_rust.core import combat as combat_mod
from iron_rust.core import shop as shop_mod
from iron_rust.core.combat import Combat
from iron_rust.core import pursuit, save_manager
from iron_rust.core.shop import buy_price, sell_price, REFUSE_REP
from iron_rust.core.status import add_status, tick_statuses, status_value
from iron_rust.entities.enemy import Enemy
from iron_rust.entities.hero import Hero
from iron_rust.quests import act2, quest as quest_mod
from iron_rust.quests.quest import Choice, Quest, StoryNode
from iron_rust.quests.companion_quests import available_arc, COMPANION_ARCS
from iron_rust.quests.side_quests import the_stagecoach
from iron_rust.data.recruits import make_recruit
from iron_rust.world.routes import world


class FakeDialogue:
    q = []

    @staticmethod
    def choose(question, options, labels=None):
        return FakeDialogue.q.pop(0) if FakeDialogue.q else options[0]

    say = narrator = success = staticmethod(lambda *a, **k: None)
    pause = divider = clear = press_enter = staticmethod(lambda *a, **k: None)
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

# --- A. Flags gate dialogue choices (Tasks 1, 2) ----------------------------
print("A. Flags / world memory")
gated = Quest(
    nodes=[
        StoryNode("n1", "start", choices=[
            Choice("Always here", "n_end"),
            Choice("Only if you helped the farmer", "n_secret",
                   condition=lambda h: h.has_flag("helped_farmer")),
        ]),
        StoryNode("n_end", "done", choices=[]),
        StoryNode("n_secret", "secret", choices=[]),
    ],
    start_id="n1",
)
h = fresh_hero()
# Without flag: only the first choice is offered (single -> auto-continue).
end = gated.play(h)
ok &= check("flag-gated choice hidden without flag", end == "n_end")
h = fresh_hero(); h.set_flag("helped_farmer")
FakeDialogue.q = [1]     # pick the now-available secret choice
end = gated.play(h)
ok &= check("flag-gated choice appears once flag is set", end == "n_secret")

# --- B. Factions + per-NPC relationships (Tasks 3, 4) -----------------------
print("\nB. Factions & relationships")
h = fresh_hero()
h.location = "silver_crossing"
FakeDialogue.q = [0]     # coach help
the_stagecoach.play(h)
ok &= check("helping raises Law faction + townsfolk rep + sets flag",
            h.faction("law") == 5 and h.town_reputation("silver_crossing") == 10 and h.has_flag("helped_stagecoach"))

h = fresh_hero(); h.location = "redemption"; h.honor = -10
act2.maybe_preacher(h, FakeDialogue)   # accept (default first option)
ok &= check("helping preacher raises ezekiel relationship", h.relationship("ezekiel") == 15)
ok &= check("...but NOT the lawman's (independent, Task 3)", h.relationship("kane") == 0)

# --- C. Active pursuit via Dijkstra (Tasks 5, 6) ----------------------------
print("\nC. Active pursuit (Dijkstra)")
h = fresh_hero(); h.location = "dust_creek"; h.wanted = 60
ok &= check("high wanted -> pursuer spawns", pursuit.should_spawn(h))
pursuit.spawn_pursuer(h, world)
start_dist = h.pursuer["distance"]
ok &= check("pursuer starts at a distance", start_dist >= 1 and h.pursuer["position"] != "dust_creek")
st = pursuit.advance_pursuer(h, world)
ok &= check("pursuer closes one step (Dijkstra)", st["distance"] < start_dist)
# Put the pursuer adjacent, then it catches on the next step.
h.pursuer["position"] = "silver_crossing"   # neighbor of dust_creek
st = pursuit.advance_pursuer(h, world)
ok &= check("pursuer reaches the hero's town -> caught", st["caught"])
h.wanted = 20
ok &= check("wanted drops -> hunter gives up", pursuit.gives_up(h) and h.pursuer is None)

# --- D. Called shots + status effects (Tasks 7, 8) --------------------------
print("\nD. Called shots & statuses")
e = Enemy("Goon", hp=40, aim=5, attack=12, threat_level=3)
add_status(e, "bleed", 2, 5)
msgs, skip = tick_statuses(e)
ok &= check("bleed ticks damage", e.hp == 35 and not skip and any("bleed" in m for m in msgs))
e.statuses.clear()
add_status(e, "stun", 1, 0)
_, skip = tick_statuses(e)
ok &= check("stun causes a skipped turn", skip)

h = fresh_hero()
e = Enemy("Goon", hp=100, aim=5, attack=12, threat_level=3)
Combat(h, [e])._resolve_called_shot(e, "arm")
ok &= check("arm shot disarms (reduces attack)", status_value(e, "disarm") > 0)
e2 = Enemy("Goon2", hp=100, aim=5, attack=12, threat_level=3)
Combat(h, [e2])._resolve_called_shot(e2, "leg")
ok &= check("leg shot stuns", any(s["type"] == "stun" for s in e2.statuses))
e3 = Enemy("Goon3", hp=100, aim=5, attack=12, threat_level=3)
Combat(h, [e3])._resolve_called_shot(e3, "head")
ok &= check("head shot causes bleed", any(s["type"] == "bleed" for s in e3.statuses))

# --- E. Dynamic economy by town rep (Task 9) --------------------------------
print("\nE. Dynamic economy")
h = fresh_hero(); h.stats["charisma"] = 0     # isolate the town factor from charisma
h.adjust_town_rep("dust_creek", -20)
ok &= check("bad town rep raises buy price (100 -> 120)", buy_price(h, 100, "dust_creek") == 120)
h2 = fresh_hero(); h2.stats["charisma"] = 0
h2.adjust_town_rep("dust_creek", 20)
ok &= check("good town rep lowers buy price (100 -> 80)", buy_price(h2, 100, "dust_creek") == 80)
h3 = fresh_hero(); h3.adjust_town_rep("dust_creek", -60)
ok &= check("robbing tanks rep below refuse threshold", h3.town_reputation("dust_creek") <= REFUSE_REP)

# --- F. Companion arcs grant permanent bonuses (Task 10) --------------------
print("\nF. Companion arcs")
h = fresh_hero()
h.gang.add_member(make_recruit("eli"))
arc = available_arc(h)
ok &= check("recruited member surfaces a companion arc", arc is not None and arc[0] == "eli")
arc[1].play(h)      # all single-choice continues
ok &= check("completing Eli's arc grants ally_damage bonus", h.has_bonus("ally_damage"))
ok &= check("ally bonus now boosts backup damage", Combat(h, [])._ally_bonus() >= 2)
ok &= check("arc no longer available once done", available_arc(h) is None)
# Kate's arc adds a Dead Eye slot.
h2 = fresh_hero(); h2.grant_bonus("deadeye_slot")
c = Combat(h2, [Enemy(f"e{i}", 50, 5, 5, i) for i in range(5)])
ranked = c.rank_targets(c.enemies)
FakeDialogue.q = [0, "head", 0, "head", 0, "head", 0, "head"]   # tag 4 targets
tags = c._tag_targets(ranked)
ok &= check("deadeye_slot lets you tag a 4th target", len(tags) == 4)

# --- G. Quest journal (Task 11) ---------------------------------------------
print("\nG. Quest journal")
h = fresh_hero()
FakeDialogue.q = [0]
the_stagecoach.play(h)
entry = h.journal.get("the_stagecoach")
ok &= check("quest logs to journal as completed", entry is not None and entry["status"] == "completed")

# --- Persistence of world memory (save round-trip) --------------------------
print("\nPersistence of world memory")
h = fresh_hero()
h.set_flag("robbed_stagecoach")
h.adjust_faction("law", -15)
h.adjust_town_rep("blackridge", -30)
h.adjust_relationship("kane", -20)
h.grant_bonus("crit_up")
h.journal_add("the_stagecoach", "The Stagecoach", "completed")
h.wanted = 60
pursuit.spawn_pursuer(h, world)
save_manager.save_game(h)
loaded = save_manager.load_game()
ok &= check("flags/factions/rep/relationship persist",
            loaded.has_flag("robbed_stagecoach") and loaded.faction("law") == -15
            and loaded.town_reputation("blackridge") == -30 and loaded.relationship("kane") == -20)
ok &= check("bonuses/journal/pursuer persist",
            loaded.has_bonus("crit_up") and loaded.journal["the_stagecoach"]["status"] == "completed"
            and loaded.pursuer is not None and loaded.pursuer["position"] == h.pursuer["position"])
save_manager.delete_save()

print("\n" + ("ALL TESTS PASSED" if ok else "SOME TESTS FAILED"))
sys.exit(0 if ok else 1)
