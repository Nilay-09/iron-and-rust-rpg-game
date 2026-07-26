"""
Active pursuit (Tasks 5, 6).

When the hero's wanted level crosses a threshold, a bounty hunter takes the
trail. Each time the hero travels, the pursuer moves one step toward the hero's
town along the shortest path (Dijkstra, from Milestone 2) — a real closing
threat. The hero evades by keeping ahead, or turns and confronts.

This module is pure logic (no UI): travel.py handles the narration and the
confrontation duel. The pursuer is stored on `hero.pursuer` as a plain dict so
it serializes with the save.
"""

from iron_rust.world.pathfinding import shortest_path

PURSUE_WANTED_THRESHOLD = 50    # wanted at/above this puts a hunter on your trail

# Law faction rep worsens things: deeply out of favor lowers the bar.
LAW_REP_MODIFIER = 10           # each -10 law rep drops the threshold by ~this


def _threshold(hero):
    law = hero.faction("law")
    # Negative law standing makes the law come for you sooner.
    return max(30, PURSUE_WANTED_THRESHOLD + (law // LAW_REP_MODIFIER))


def should_spawn(hero):
    return hero.pursuer is None and hero.wanted >= _threshold(hero)


def spawn_pursuer(hero, world):
    """Start a pursuer at the town farthest from the hero (via Dijkstra)."""
    farthest, best = hero.location, -1
    for town in world.towns():
        if town == hero.location:
            continue
        _, cost = shortest_path(world, hero.location, town)
        if cost != float("inf") and cost > best:
            best, farthest = cost, town

    hero.pursuer = {
        "name": "Bounty Hunter Wade",
        "position": farthest,
        "distance": best if best > 0 else 0,
    }
    return hero.pursuer


def gives_up(hero):
    """If the hero is no longer wanted enough, the hunter loses interest."""
    if hero.pursuer is not None and hero.wanted < _threshold(hero) - 10:
        hero.pursuer = None
        return True
    return False


def advance_pursuer(hero, world):
    """
    Move the pursuer one step toward the hero along the shortest path.
    Returns {"caught": bool, "position": str, "distance": number}, or None.
    """
    p = hero.pursuer
    if p is None:
        return None

    path, _ = shortest_path(world, p["position"], hero.location)
    if not path:
        # Can't reach the hero at all (shouldn't happen on a connected map).
        p["distance"] = 99
        return {"caught": False, "position": p["position"], "distance": 99}
    if len(path) <= 1:
        # Already on top of the hero.
        p["distance"] = 0
        return {"caught": True, "position": p["position"], "distance": 0}

    p["position"] = path[1]                    # one step along the Dijkstra path
    _, dist = shortest_path(world, p["position"], hero.location)
    p["distance"] = dist if dist != float("inf") else 99
    caught = p["position"] == hero.location
    return {"caught": caught, "position": p["position"], "distance": p["distance"]}


def clear_pursuer(hero):
    hero.pursuer = None
