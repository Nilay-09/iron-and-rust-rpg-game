import random

from iron_rust.entities.enemy import Enemy

# Same stat-dict pattern as archetypes.py.
ENEMIES = {
    "bandit": {
        "name": "Bandit",
        "hp": 30,
        "aim": 5,
        "attack": 8,
        "threat_level": 2,
    },
    "lawman": {
        "name": "Corrupt Lawman",
        "hp": 45,
        "aim": 7,
        "attack": 11,
        "threat_level": 3,
    },
    "rival_gunslinger": {
        "name": "Rival Gunslinger",
        "hp": 40,
        "aim": 9,
        "attack": 14,
        "threat_level": 5,
    },
    # Act 3 boss: the betrayer. Far stronger than any road encounter.
    "rourke": {
        "name": "Rourke",
        "hp": 120,
        "aim": 12,
        "attack": 20,
        "threat_level": 10,
    },
    # A relentless bounty hunter — the pursuit's confrontation fight.
    "bounty_hunter": {
        "name": "Bounty Hunter",
        "hp": 70,
        "aim": 10,
        "attack": 16,
        "threat_level": 7,
    },
}


def spawn_betrayer():
    """The climax enemy for Act 3 — Rourke, the man who left you for dead."""
    return spawn("rourke")


def spawn(key, name=None):
    """Build a fresh Enemy from a template key."""
    data = ENEMIES[key]
    return Enemy(
        name=name or data["name"],
        hp=data["hp"],
        aim=data["aim"],
        attack=data["attack"],
        threat_level=data["threat_level"],
    )


def spawn_for_danger(danger):
    """
    Pull an enemy (or a small pack on the meanest roads) suited to a town's
    danger rating. Returns a list of Enemy.
    """
    if danger <= 1:
        pool = ["bandit"]
    elif danger == 2:
        pool = ["bandit", "bandit", "lawman"]
    elif danger == 3:
        pool = ["bandit", "lawman"]
    elif danger == 4:
        pool = ["lawman", "rival_gunslinger"]
    else:
        pool = ["rival_gunslinger", "lawman"]

    enemies = [spawn(random.choice(pool))]

    # On the worst roads, trouble sometimes comes in pairs.
    if danger >= 4 and random.random() < 0.5:
        enemies.append(spawn(random.choice(["bandit", "lawman"])))

    return enemies
