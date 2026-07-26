"""
Act 1: The Fall.

The opening betrayal, authored as story data for the Quest engine. It is a
linear chain of narration nodes — no player choices yet — each carrying the
player forward with a single "Continue", ending on a node with no choices.

Also here: `the_crossroads`, a small optional quest with a real fork, used to
prove that branching and honor/wanted changes actually work.
"""

from iron_rust.core.combat import start_duel
from iron_rust.data.dialogues import DIALOGUES
from iron_rust.data.enemies import spawn_betrayer
from iron_rust.quests.endings import ENDINGS, determine_ending
from iron_rust.quests.quest import Choice, Quest, StoryNode
from iron_rust.ui.dialogue import Dialogue


# ----------------------------------------------------------------------
# The Fall — a linear betrayal. Honor is untouched all the way through.
# ----------------------------------------------------------------------

the_fall = Quest(
    title="The Fall",
    start_id="fall_1",
    nodes=[
        StoryNode(
            id="fall_1",
            text=(
                "It began with a promise and a plan. Rourke swore the payroll "
                "train out of Silver Crossing was soft — one guard, a sleepy "
                "engineer, and gold enough to set the whole crew free for life."
            ),
            choices=[Choice("Continue", "fall_2")],
        ),
        StoryNode(
            id="fall_2",
            text=(
                "You rode with them for three years. You trusted Rourke like "
                "blood. So when he handed you the detonator and sent you down "
                "the tracks alone, you did not think twice."
            ),
            choices=[Choice("Continue", "fall_3")],
        ),
        StoryNode(
            id="fall_3",
            text=(
                "The charge blew. The train screamed to a halt. And as you "
                "climbed toward the strongbox, you heard the crew's horses "
                "turning — not toward you, but away."
            ),
            choices=[Choice("Continue", "fall_4")],
        ),
        StoryNode(
            id="fall_4",
            text=(
                "Rourke was smiling when he shot you. The slug took you in the "
                "shoulder and threw you off the car. The last thing you saw was "
                "the gold, and his back, and the dust closing over both."
            ),
            choices=[Choice("Continue", "fall_end")],
        ),
        StoryNode(
            id="fall_end",
            text=(
                "You wake in the bed of a stranger's wagon, half-dead, rolling "
                "into Dust Creek. You have no crew, no gold, and no name worth "
                "trusting. Only a debt — and the long road it will take to "
                "collect it."
            ),
            # No choices: this is where Act 1 ends and the recursion stops.
            choices=[],
        ),
    ],
)


# ----------------------------------------------------------------------
# The Crossroads — an optional fork that actually moves honor and wanted.
# ----------------------------------------------------------------------

the_crossroads = Quest(
    title="The Crossroads",
    start_id="cross_1",
    nodes=[
        StoryNode(
            id="cross_1",
            text=(
                "A mile out of town you find a man face-down in the ruts, robbed "
                "and bleeding, one hand reaching for a coin purse that spilled "
                "just out of his grasp. He looks up at you and tries to speak."
            ),
            choices=[
                Choice(
                    "Bind his wounds and share your water.",
                    "cross_help",
                    honor_change=10,
                ),
                Choice(
                    "Take the purse and ride on.",
                    "cross_rob",
                    honor_change=-10,
                    wanted_change=5,
                ),
            ],
        ),
        StoryNode(
            id="cross_help",
            text=(
                "You get him upright and walking. He gives you his name and a "
                "promise to remember yours. Word of the deed rides ahead of you "
                "into the next town."
            ),
            choices=[],
        ),
        StoryNode(
            id="cross_rob",
            text=(
                "The purse is heavier than it looks. You leave him in the dirt "
                "and do not look back. Somewhere behind you, a lawman starts "
                "writing down a description."
            ),
            choices=[],
        ),
    ],
)


# ----------------------------------------------------------------------
# Act 3: The Reckoning — the lead-up to the final duel with the betrayer.
# ----------------------------------------------------------------------

the_reckoning = Quest(
    title="The Reckoning",
    start_id="reck_1",
    nodes=[
        StoryNode(
            id="reck_1",
            text=(
                "The word finds you in a rain-dark saloon: Rourke is holed up at "
                "Dead Man's Pass, sitting on the old payroll gold and a crew gone "
                "soft on easy money. After all these miles, the trail finally "
                "points one way."
            ),
            choices=[Choice("Continue", "reck_2")],
        ),
        StoryNode(
            id="reck_2",
            text=(
                "You ride through the night and leave the horse at the canyon "
                "mouth. The Pass is quiet — too quiet — the way a room goes still "
                "when everyone's already looking at you."
            ),
            choices=[Choice("Continue", "reck_3")],
        ),
        StoryNode(
            id="reck_3",
            text=(
                "Rourke steps out onto the porch like he's been waiting years. "
                "Maybe he has. He looks at the scar he gave you and smiles that "
                "same old smile. \"You should've stayed dead.\" His hand drifts "
                "toward his iron."
            ),
            # Terminal: the lead-up ends, the duel begins.
            choices=[],
        ),
    ],
)

# Every epilogue as a terminal StoryNode, keyed by ending id. Text lives in
# data/dialogues.py so all the honor/wanted payoff is authored in one place.
epilogues = Quest(
    title="Epilogue",
    start_id="drifter",
    nodes=[
        StoryNode(id=key, text=DIALOGUES["endings"][key], choices=[])
        for key in DIALOGUES["endings"]
    ],
)


# The final moral choice — spare or kill the betrayer. Shifts honor/wanted right
# before the ending is decided, so it can tip which epilogue you get.
the_verdict = Quest(
    title="The Verdict",
    start_id="verdict_1",
    nodes=[
        StoryNode(
            id="verdict_1",
            text=(
                "Rourke is on his knees in the dust, his gun spun away, blood at "
                "his mouth and that smile finally gone. His life is yours now — "
                "to take, or to hand to the law."
            ),
            choices=[
                Choice(
                    "Put him down. This was always about the bullet.",
                    "verdict_kill",
                    honor_change=-10,
                    wanted_change=10,
                ),
                Choice(
                    "Drag him to the marshal alive. Let the law have him.",
                    "verdict_law",
                    honor_change=15,
                    wanted_change=-10,
                ),
            ],
        ),
        StoryNode(
            id="verdict_kill",
            text=(
                "You don't say anything. There's nothing left to say. One shot, "
                "and the man who left you for dead is just another body in the "
                "dust of Dead Man's Pass. The debt is paid in the only currency "
                "you both ever trusted."
            ),
            choices=[],
        ),
        StoryNode(
            id="verdict_law",
            text=(
                "You holster your iron and haul him up by the collar. Let him "
                "hang sober and sorry in front of the whole territory. Some "
                "reckonings are louder than a gunshot — and you want witnesses."
            ),
            choices=[],
        ),
    ],
)


def _play_epilogue(hero, ending):
    meta = ENDINGS[ending]
    Dialogue.divider()
    Dialogue.panel("YOUR STORY ENDS", meta["title"])
    epilogues.play(hero, ending)      # narrate the matching epilogue node


def play_act3(hero):
    """
    Run the Reckoning: the lead-up narration, the boss duel against the
    betrayer (with gang backup if morale is high enough), then the ending that
    the hero's honor/wanted/gang have earned.

    Returns the ending key, or None if the hero fled the final duel — in which
    case the reckoning is postponed rather than resolved (no ending yet).
    """
    the_reckoning.play(hero)

    boss = spawn_betrayer()
    gang = getattr(hero, "gang", None)
    allies = [gang.best_backup()] if (gang is not None and gang.backup_ready) else []

    result = start_duel(hero, boss, allies=allies)

    if result == "fled":
        # You can run from a road duel, but not from this — it just waits.
        Dialogue.divider()
        Dialogue.say(
            "You break off and ride into the dark. But Rourke isn't going "
            "anywhere, and neither is what he owes you. This isn't over."
        )
        Dialogue.pause(0.6)
        return None

    if result == "defeat":
        # Task 6: defeat is its own ending — not just a dead end.
        ending = "died_boots"
    else:
        the_verdict.play(hero)              # final moral choice tips honor/wanted
        ending = determine_ending(hero)

    _play_epilogue(hero, ending)
    return ending
