import random


class Gang:
    """
    The hero's camp: a roster of members, a shared pot of funds, morale, and
    bought upgrades.

    Morale is the health of the camp (0-100). Contributions raise it; neglect
    (travelling without paying in) lets it slip — and a member with low morale
    can desert. High morale is what convinces a member to ride out as backup.
    """

    MORALE_MIN, MORALE_MAX = 0, 100
    FUNDS_PER_MORALE = 5          # $5 into the pot -> +1 morale
    BACKUP_THRESHOLD = 60         # morale at/above this unlocks a duel backup
    DESERT_MORALE = 25            # below this, members may walk

    def __init__(self, name, members=None, funds=0, morale=50, upgrades=None):
        self.name = name
        self.members = members or []
        self.funds = funds
        self.morale = morale
        self.upgrades = set(upgrades) if upgrades else set()

    def add_member(self, member):
        self.members.append(member)
        return member

    def contribute(self, amount):
        """Add money to the pot and raise morale proportionally. Returns morale gained."""
        amount = max(0, int(amount))
        self.funds += amount
        return self.adjust_morale(amount // self.FUNDS_PER_MORALE)

    def adjust_morale(self, amount):
        """Shift morale, clamped to [MORALE_MIN, MORALE_MAX]. Returns the delta applied."""
        before = self.morale
        self.morale = max(self.MORALE_MIN, min(self.MORALE_MAX, self.morale + amount))
        return self.morale - before

    @property
    def backup_ready(self):
        """True when morale is high enough and there's someone to send."""
        return bool(self.members) and self.morale >= self.BACKUP_THRESHOLD

    def best_backup(self):
        """The most loyal member, or None. Who rides out when morale is high."""
        if not self.members:
            return None
        return max(self.members, key=lambda m: getattr(m, "loyalty", 0))

    def has_upgrade(self, key):
        return key in self.upgrades

    def buy_upgrade(self, key, cost):
        """Spend funds on an upgrade. Returns True on success."""
        if key in self.upgrades or self.funds < cost:
            return False
        self.funds -= cost
        self.upgrades.add(key)
        return True

    def check_desertion(self):
        """
        Task 17: when morale is low, the least-loyal member may walk. Returns the
        deserter (removed from the roster) or None. The lower the morale, the
        likelier it is.
        """
        if not self.members or self.morale >= self.DESERT_MORALE:
            return None
        # Chance grows as morale falls below the threshold.
        chance = (self.DESERT_MORALE - self.morale) / 100
        if random.random() >= chance:
            return None
        deserter = min(self.members, key=lambda m: getattr(m, "loyalty", 0))
        self.members.remove(deserter)
        return deserter
