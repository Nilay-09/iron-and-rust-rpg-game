"""
Combat status effects (Task 8).

A status is a dict {type, turns, value} living on an entity's `.statuses` list.
Ticked at the start of each combatant's turn:

  bleed  - loses `value` HP each turn (damage over time)
  stun   - skips this turn
  disarm - deals reduced damage (read by the attack code, `value` = reduction)
"""


def add_status(entity, kind, turns, value=0):
    """Add a status, refreshing an existing one of the same kind to the stronger."""
    for s in entity.statuses:
        if s["type"] == kind:
            s["turns"] = max(s["turns"], turns)
            s["value"] = max(s["value"], value)
            return
    entity.statuses.append({"type": kind, "turns": turns, "value": value})


def has_status(entity, kind):
    return any(s["type"] == kind for s in entity.statuses)


def status_value(entity, kind):
    return max((s["value"] for s in entity.statuses if s["type"] == kind), default=0)


def tick_statuses(entity):
    """
    Apply and age an entity's statuses. Returns (messages, skip_turn).
    Call at the start of the entity's turn.
    """
    messages = []
    skip = False

    for s in list(entity.statuses):
        if s["type"] == "bleed":
            dmg = s["value"]
            entity.hp = max(0, entity.hp - dmg)
            messages.append(f"bleeds for {dmg}")
        elif s["type"] == "stun":
            skip = True
            messages.append("is stunned and can't act")

        s["turns"] -= 1
        if s["turns"] <= 0:
            entity.statuses.remove(s)

    return messages, skip
