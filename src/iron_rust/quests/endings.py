"""
Act 3 endings.

determine_ending(hero) weighs the hero's honor and wanted level — and, for the
secret ending, the loyalty of their gang (morale) — against thresholds to pick
which epilogue the Reckoning pays off with.
"""

# Thresholds.
HIGH_HONOR = 50
LOW_HONOR = -20
CLEAN_WANTED = 40      # below this you're not really hunted
HIGH_WANTED = 55       # at/above this you're notorious
SECRET_HONOR = 60      # Outlaw King needs to be beloved...
SECRET_WANTED = 70     # ...and badly wanted...
SECRET_MORALE = 60     # ...with a gang that would die for them.

# Ending key -> presentation metadata. epilogue_key indexes DIALOGUES["endings"].
ENDINGS = {
    "outlaw_king": {"title": "Outlaw King", "epilogue_key": "outlaw_king"},
    "redemption": {"title": "Redemption", "epilogue_key": "redemption"},
    "hunted_down": {"title": "Hunted Down", "epilogue_key": "hunted_down"},
    "legend": {"title": "Legend", "epilogue_key": "legend"},
    "gang_leader": {"title": "The Gang Leader", "epilogue_key": "gang_leader"},
    "drifter": {"title": "The Drifter", "epilogue_key": "drifter"},
    "died_boots": {"title": "Died With Your Boots On", "epilogue_key": "died_boots"},
}


def determine_ending(hero):
    """
    Return an ending key from the hero's final honor, wanted, and gang state.

    Task 22: gang state is a real factor now — the secret Outlaw King ending
    demands a loyal gang at your back, and a hero who built a loyal following
    but stayed out of the extremes earns The Gang Leader instead of fading out.
    A gang that deserted you disqualifies both.
    """
    honor = getattr(hero, "honor", 0)
    wanted = getattr(hero, "wanted", 0)
    gang = getattr(hero, "gang", None)
    morale = getattr(gang, "morale", 0)
    members = len(getattr(gang, "members", []) or [])
    deserters = getattr(hero, "gang_deserters", 0)

    # A gang that stuck with you: at least one member, nobody walked, morale high.
    loyal_gang = members >= 1 and deserters == 0 and morale >= SECRET_MORALE

    # Secret ending: a folk-hero criminal — loved, hunted, and well-followed.
    if honor >= SECRET_HONOR and wanted >= SECRET_WANTED and loyal_gang:
        return "outlaw_king"

    # High honor and not truly hunted: you made it right.
    if honor >= HIGH_HONOR and wanted < CLEAN_WANTED:
        return "redemption"

    # Low honor and badly wanted: the law (or worse) catches up.
    if honor <= LOW_HONOR and wanted >= HIGH_WANTED:
        return "hunted_down"

    # Notorious either way — remembered in song and story.
    if wanted >= HIGH_WANTED:
        return "legend"

    # Not extreme, but you built something that lasted: a loyal gang.
    if loyal_gang:
        return "gang_leader"

    # Nothing extreme, no one at your back: you fade into the dust.
    return "drifter"
