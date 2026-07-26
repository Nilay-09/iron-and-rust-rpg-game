"""
Companion arcs (Task 10).

Each recruited member has a short personal quest revealing their backstory.
Completing it grants a permanent bonus instead of leaving them a generic unit:

  eli   -> ally_damage   (gang backup hits harder)
  doc   -> shop_discount (10% off everywhere)
  kate  -> deadeye_slot  (tag a 4th Dead Eye target)
  silas -> crit_up       (better crit chance)

Bonuses are read by combat (ally_damage, deadeye_slot, crit_up) and shop
(shop_discount).
"""

from iron_rust.quests.quest import Choice, Quest, StoryNode


def _grant(bonus_key):
    def effect(hero):
        hero.grant_bonus(bonus_key)
        hero.set_flag(f"companion_{bonus_key}")
    return effect


def _arc(qid, title, bonus, beats, finale):
    """Build a short linear backstory quest ending with a bonus-granting choice."""
    nodes = []
    for i, text in enumerate(beats):
        nodes.append(StoryNode(id=f"{qid}_{i}", text=text,
                               choices=[Choice("Continue", f"{qid}_{i + 1}")]))
    # The last continuation grants the bonus, then a terminal beat.
    nodes.append(StoryNode(
        id=f"{qid}_{len(beats)}", text=finale,
        choices=[Choice("Continue", f"{qid}_end", effect=_grant(bonus))]))
    nodes.append(StoryNode(id=f"{qid}_end", text="You ride on, a little closer than before.", choices=[]))
    return Quest(nodes, start_id=f"{qid}_0", title=title, journal_id=qid)


COMPANION_ARCS = {
    "eli": {
        "bonus": "ally_damage",
        "quest": _arc(
            "eli_arc", "Eli's Debt", "ally_damage",
            beats=[
                "Around the fire, Eli finally talks. He had a brother on that "
                "payroll train — younger, greener. Rourke's double-cross buried "
                "him too. Eli's been hunting a reckoning as long as you have.",
                "He asks you to ride to the brother's unmarked grave with him, "
                "out past the salt flats, so he doesn't have to do it alone.",
            ],
            finale=(
                "You stand with Eli over the grave while he says his piece. When "
                "he turns back, something's settled in him — a steadier hand and "
                "a colder aim. He fights harder at your side now."
            ),
        ),
    },
    "doc": {
        "bonus": "shop_discount",
        "quest": _arc(
            "doc_arc", "Doc's Ledger", "shop_discount",
            beats=[
                "Doc Weller was an army surgeon once, until he sold morphine he "
                "shouldn't have to men who needed it. He's been paying it off in "
                "guilt ever since — and in favors owed all across the territory.",
                "He asks you to help him settle the last of those old debts, "
                "quietly, town by town.",
            ],
            finale=(
                "With his ledger finally clean, Doc's name opens doors again. The "
                "merchants who owed him now owe you — and it shows at the till."
            ),
        ),
    },
    "kate": {
        "bonus": "deadeye_slot",
        "quest": _arc(
            "kate_arc", "Kate's Fuse", "deadeye_slot",
            beats=[
                "Dynamite Kate learned her trade blasting rock for the very "
                "railroad that's hunting you both. She left the day a cave-in she "
                "warned them about killed six men they wouldn't pull out.",
                "She wants to blow the company's supply depot — not for money, "
                "for the six. She needs a steady gun while she sets the charges.",
            ],
            finale=(
                "The depot goes up in a sunrise of fire. Kate watches it burn with "
                "dry eyes, then teaches you a trick of timing that lets you paint "
                "one more target when the world slows down."
            ),
        ),
    },
    "silas": {
        "bonus": "crit_up",
        "quest": _arc(
            "silas_arc", "Silas's Eye", "crit_up",
            beats=[
                "Silas Bone never misses, and it costs him sleep. He was a "
                "sharpshooter in a war he won't name, and every man he dropped "
                "still lines up behind his eyes when he closes them.",
                "He asks you to sit with him through one bad night, no questions.",
            ],
            finale=(
                "By dawn the ghosts have thinned a little. Silas cleans his rifle "
                "with steadier hands and shows you how he finds the killing line — "
                "your own shots bite deeper now."
            ),
        ),
    },
}


def available_arc(hero):
    """Return (recruit_key, quest) for an un-done arc of a current member, or None."""
    member_specials = {getattr(m, "special", None) for m in hero.gang.members}
    special_to_key = {"cover_fire": "eli", "field_medic": "doc",
                      "dynamite": "kate", "sharpshooter": "silas"}
    for special in member_specials:
        key = special_to_key.get(special)
        if key and key in COMPANION_ARCS:
            bonus = COMPANION_ARCS[key]["bonus"]
            if not hero.has_bonus(bonus):
                return key, COMPANION_ARCS[key]["quest"]
    return None
