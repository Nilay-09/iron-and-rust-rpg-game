"""
Side quests with real stakes — each rewards money, items, or a gang recruit,
and each carries an honor/wanted consequence either way.

`the_reunion` ties back to the Act 1 betrayal (recruit Eli). The others let the
player build the gang (Doc, Kate) and their purse while shaping reputation.
"""

from iron_rust.data.recruits import make_recruit
from iron_rust.quests.quest import Choice, Quest, StoryNode


# -- effect factories (Choice.effect callables) ------------------------------

def _money(amount):
    def effect(hero):
        hero.money = max(0, hero.money + amount)
    return effect


def _item(key, qty=1):
    def effect(hero):
        hero.add_item(key, qty)
    return effect


def _recruit(key):
    def effect(hero):
        hero.gang.add_member(make_recruit(key))
    return effect


def _all(*effects):
    def effect(hero):
        for e in effects:
            e(hero)
    return effect


def _flag(name):
    def effect(hero):
        hero.set_flag(name)
    return effect


def _townsfolk(amount):
    """Adjust townsfolk reputation in the hero's current town."""
    def effect(hero):
        hero.adjust_town_rep(hero.location, amount)
    return effect


def _faction(name, amount):
    def effect(hero):
        hero.adjust_faction(name, amount)
    return effect


# -- The Reunion — recruit Eli (survivor of the betrayal) --------------------

the_reunion = Quest(
    title="The Reunion",
    journal_id="the_reunion",
    start_id="reunion_1",
    nodes=[
        StoryNode(
            id="reunion_1",
            text=(
                "In the back of a half-burned way station you find a man cleaning "
                "a rifle by feel, one eye swollen shut. Eli Vance — he rode the "
                "payroll job too. Rourke left him for dead in the same dust."
            ),
            choices=[
                Choice("\"Get up, Eli. We ride together now.\"", "reunion_join",
                       honor_change=5, effect=_all(_recruit("eli"), _faction("gang", 10))),
                Choice("Some debts you settle alone. Ride on.", "reunion_pass"),
            ],
        ),
        StoryNode(id="reunion_join", text=(
            "Eli spits out a tooth and grins red. \"Thought you were a ghost.\" "
            "He slings the rifle and follows you out."), choices=[]),
        StoryNode(id="reunion_pass", text=(
            "You leave him to his rifle and his one good eye. You ride on alone."),
            choices=[]),
    ],
)


# -- The Stagecoach — money vs. money+notoriety ------------------------------

the_stagecoach = Quest(
    title="The Stagecoach",
    journal_id="the_stagecoach",
    start_id="coach_1",
    nodes=[
        StoryNode(
            id="coach_1",
            text=(
                "A stagecoach lies stranded ahead, axle broken, bandits circling "
                "like flies. The driver waves you down — but that strongbox on the "
                "back would fund your whole war."
            ),
            choices=[
                Choice("Drive the bandits off and fix the axle.", "coach_help",
                       honor_change=10,
                       effect=_all(_money(80), _flag("helped_stagecoach"),
                                   _townsfolk(10), _faction("law", 5))),
                Choice("Take the strongbox yourself.", "coach_rob",
                       honor_change=-15, wanted_change=15,
                       effect=_all(_money(150), _flag("robbed_stagecoach"),
                                   _townsfolk(-20), _faction("law", -15))),
            ],
        ),
        StoryNode(id="coach_help", text=(
            "You scatter the bandits and get the wheel turning. The grateful "
            "driver presses $80 into your hand and your name into his prayers."),
            choices=[]),
        StoryNode(id="coach_rob", text=(
            "You crack the box and ride off $150 richer. The driver's screams "
            "follow you, and so, soon enough, will the law."), choices=[]),
    ],
)


# -- The Field Medic — recruit Doc, or loot his supplies ---------------------

the_field_medic = Quest(
    title="The Field Medic",
    journal_id="the_field_medic",
    start_id="medic_1",
    nodes=[
        StoryNode(
            id="medic_1",
            text=(
                "An old army surgeon named Doc Weller is pinned down by debt "
                "collectors outside a shuttered clinic. He offers his skills to "
                "anyone who'll clear his slate — or you could just take his kit."
            ),
            choices=[
                # Only offered if you can actually cover the $40 debt.
                Choice("Pay off his $40 debt; he joins your gang.", "medic_join",
                       honor_change=10,
                       effect=_all(_money(-40), _recruit("doc"), _faction("gang", 10)),
                       condition=lambda h: h.money >= 40),
                Choice("Rob the clinic of its medical supplies.", "medic_rob",
                       honor_change=-10, wanted_change=5,
                       effect=_all(_item("medkit", 2), _townsfolk(-15))),
                # Always available, so a broke player is never forced to rob.
                Choice("Leave him to his troubles and ride on.", "medic_pass"),
            ],
        ),
        StoryNode(id="medic_join", text=(
            "You settle Doc's debt with $40 and a hard look at the collectors. "
            "He packs his bag. \"Try not to get shot,\" he says. \"But if you do — "
            "I'm your man.\""), choices=[]),
        StoryNode(id="medic_rob", text=(
            "You clean out the clinic — two field medkits richer, one more town "
            "that spits at your name."), choices=[]),
        StoryNode(id="medic_pass", text=(
            "You've no money to spare and no stomach to rob a doctor. You wish "
            "him luck and ride on."), choices=[]),
    ],
)


# -- The Powder Run — recruit Kate, or take the payout -----------------------

the_powder_run = Quest(
    title="The Powder Run",
    journal_id="the_powder_run",
    start_id="powder_1",
    nodes=[
        StoryNode(
            id="powder_1",
            text=(
                "Dynamite Kate needs a partner to run a wagon of blasting powder "
                "past a company checkpoint. Pull it off and she'll ride with you. "
                "Or sell her out to the company for a fat finder's fee."
            ),
            choices=[
                Choice("Run the checkpoint with her.", "powder_join",
                       honor_change=5, wanted_change=5,
                       effect=_all(_recruit("kate"), _faction("gang", 5))),
                Choice("Sell her out for the reward.", "powder_betray",
                       honor_change=-15,
                       effect=_all(_money(120), _flag("betrayed_kate"), _faction("gang", -20))),
            ],
        ),
        StoryNode(id="powder_join", text=(
            "You bluff the checkpoint and gun the wagon through in a cloud of "
            "dust. Kate whoops and slaps your back. \"We're gonna get along fine.\""),
            choices=[]),
        StoryNode(id="powder_betray", text=(
            "The company pays out $120 for Kate's whereabouts. You don't stay to "
            "watch them take her. You tell yourself that means something."),
            choices=[]),
    ],
)


# Everything the trail can throw at you, for the travel encounter roller.
SIDE_QUESTS = [the_reunion, the_stagecoach, the_field_medic, the_powder_run]
