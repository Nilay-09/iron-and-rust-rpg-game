from .person import Person


class NPC(Person):
    """
    A non-player character. Doubles as a gang member: `role` describes their
    part in a fight ("backup gunslinger", "medic"), `special` is their unique
    combat ability, `loyalty` scales performance and resists desertion, and
    `hp` lets them stand in the combat turn queue.
    """

    def __init__(self, name, age, gender, role, disposition="neutral",
                 loyalty=50, hp=50, special=None):
        super().__init__(name, age, gender, role)
        self.disposition = disposition
        self.loyalty = loyalty
        self.hp = hp
        self.special = special
