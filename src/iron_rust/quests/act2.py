"""
Act 2 — The Territory.

Two recurring characters who react to the hero's choices:

  * Marshal Kane (the lawman arc) appears in the law-abiding towns and escalates
    with the hero's `wanted` level — a tip of the hat, then a warning, then a duel.
  * Father Ezekiel (the preacher arc) appears in the quiet towns when `honor` is
    low, offering low-honor players a real path back up.

Both are wired into arrivals in travel.py.
"""

from iron_rust.core.combat import start_duel
from iron_rust.data.enemies import spawn
from iron_rust.ui.dialogue import Dialogue

LAW_TOWNS = {"silver_crossing", "iron_forge", "blackridge"}
REDEMPTION_TOWNS = {"redemption", "dust_creek"}


def maybe_lawman(hero, dialogue=Dialogue):
    """Marshal Kane — reacts to the hero's wanted level, once per law town."""
    town = getattr(hero, "location", None)
    if town not in LAW_TOWNS:
        return

    flag = f"kane_seen_{town}"
    if flag in hero.story_flags:
        return
    hero.story_flags.add(flag)

    wanted = hero.wanted
    dialogue.divider()

    # Task 2: Kane references specific things you've done, not just a number.
    if hero.has_flag("robbed_stagecoach"):
        dialogue.say("\"That stagecoach driver out on the flats? He described you "
                     "real well,\" Kane says. \"I don't forget a thing like that.\"")
        hero.adjust_relationship("kane", -5)
    elif hero.has_flag("helped_stagecoach"):
        dialogue.say("\"Heard you pulled that stranded coach out of a bad spot,\" "
                     "Kane allows. \"That buys you a little rope with me.\"")
        hero.adjust_relationship("kane", 5)

    if wanted < 20:
        dialogue.say(
            "Marshal Kane tips his hat as you pass. \"Keep it clean in my town, "
            "stranger, and we'll have no trouble.\""
        )
        hero.adjust_relationship("kane", 2)
    elif wanted < 50:
        hero.story_flags.add("kane_warned")
        dialogue.say(
            "Marshal Kane steps into your path. \"I've seen your face on paper, "
            "friend. Consider this the only warning you'll get.\""
        )
    else:
        dialogue.say(
            "Marshal Kane's hand is already on his iron. \"You're worth more to "
            "me dead than alive now. This ends here.\""
        )
        allies = [hero.gang.best_backup()] if hero.gang.backup_ready else []
        result = start_duel(hero, spawn("lawman", name="Marshal Kane"), allies=allies)
        if result == "victory":
            hero.adjust_wanted(-25)
            hero.adjust_relationship("kane", -20)   # per-NPC (Task 3)
            hero.adjust_faction("law", -15)         # faction (Task 4)
            hero.story_flags.add("kane_beaten")
            dialogue.say("Kane goes down in the street. The bounty on you cools — for now.")
        elif result == "defeat":
            hero.hp = max(hero.hp, 20)
            hero.adjust_wanted(-10)
            dialogue.say("Kane's shot puts you down, but he leaves you breathing. Barely.")
        else:  # fled
            dialogue.say("You slip Kane in the alleys. He'll be looking for you now.")

    dialogue.pause(0.6)


def maybe_preacher(hero, dialogue=Dialogue):
    """Father Ezekiel — offers redemption to low-honor heroes in quiet towns."""
    town = getattr(hero, "location", None)
    if town not in REDEMPTION_TOWNS:
        return
    if hero.honor >= 0 or "preacher_done" in hero.story_flags:
        return

    dialogue.divider()
    # Task 2: Ezekiel references a specific deed if you did one.
    if hero.has_flag("helped_stagecoach"):
        dialogue.say("\"Word travels. They say you saved souls on the flats road,\" "
                     "Ezekiel says softly. \"There's more of that road in you yet.\"")

    dialogue.say(
        "Father Ezekiel studies the hard set of your face. \"There is a road "
        "back, son, for any man who'll walk it. Will you?\""
    )
    choice = dialogue.choose(
        "The preacher offers you a chance at grace.",
        ["accept", "refuse"],
        labels={
            "accept": "Help rebuild the mission — walk the road back (+honor)",
            "refuse": "Turn from the church and ride on",
        },
    )
    if choice == "accept":
        hero.adjust_honor(15)
        hero.adjust_relationship("ezekiel", 15)     # per-NPC, independent of Kane (Task 3)
        hero.set_flag("helped_preacher")
        hero.story_flags.add("preacher_done")
        dialogue.say(
            "You spend days raising the burned chapel's beams. Something in you "
            "eases that hasn't in years. Honor +15."
        )
    else:
        dialogue.say("You turn from the church. Some men aren't ready to be saved.")

    dialogue.pause(0.6)
