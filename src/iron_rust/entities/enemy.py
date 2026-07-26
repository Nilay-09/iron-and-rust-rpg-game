class Enemy:
    """
    A combatant the hero faces in a duel.

    aim          - accuracy stat, rolled against to land shots
    attack       - base damage dealt on a hit
    threat_level - how dangerous; Dead Eye targeting ranks against this
    """

    def __init__(self, name, hp, aim, attack, threat_level=1):
        self.name = name
        self.hp = hp
        self.aim = aim
        self.attack = attack
        self.threat_level = threat_level
        self.statuses = []          # combat status effects (Milestone 8)

    @property
    def alive(self):
        return self.hp > 0

    def __repr__(self):
        return f"Enemy({self.name!r}, hp={self.hp}, threat={self.threat_level})"
