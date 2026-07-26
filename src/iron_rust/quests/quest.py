"""
A tiny branching-story engine.

A Quest is a graph of StoryNodes. Each node shows some narration and offers
choices; a choice carries the player to another node and may shift honor and
wanted. play() walks the graph recursively until it reaches a node with no
choices — that's a terminal (ending) node.
"""

from dataclasses import dataclass, field

from iron_rust.ui.dialogue import Dialogue, console


@dataclass
class Choice:
    """One branch out of a node."""
    label: str                  # what the player sees
    next_id: str                # id of the node this leads to
    honor_change: int = 0       # applied to hero.honor when chosen
    wanted_change: int = 0      # applied to hero.wanted when chosen
    effect: object = None       # optional callable(hero) for side effects (e.g. recruit)
    condition: object = None    # optional callable(hero) -> bool; gates the choice (Tasks 1, 2)


@dataclass
class StoryNode:
    """A single beat of story. No choices == an ending."""
    id: str
    text: str
    choices: list = field(default_factory=list)


class Quest:
    """
    Holds the nodes and a starting id, and plays them out.

    nodes may be a dict {id: StoryNode} or a list/tuple of StoryNodes (which is
    indexed by id automatically).
    """

    def __init__(self, nodes, start_id, title=None, journal_id=None):
        if isinstance(nodes, (list, tuple)):
            nodes = {node.id: node for node in nodes}
        self.nodes = nodes
        self.start_id = start_id
        self.title = title
        self.journal_id = journal_id      # if set, logs to the hero's journal (Task 11)

    def play(self, hero, node_id=None):
        """
        Show the node, take a choice, apply its honor/wanted changes, and recurse
        into the next node. Stops when it reaches a node with no choices, returning
        that terminal node's id.
        """
        # Task 11: log an active journal entry the first time the quest is entered.
        if node_id is None and self.journal_id:
            hero.journal_add(self.journal_id, self.title or self.journal_id, "active")

        node = self.nodes[node_id or self.start_id]

        self._narrate(node)

        if not node.choices:
            if self.journal_id:
                hero.journal_update(self.journal_id, status="completed")
            return node.id                      # recursion bottoms out here

        choice = self._decide(hero, node)
        self._apply(hero, choice)

        return self.play(hero, choice.next_id)  # walk to the next beat

    # -- presentation ---------------------------------------------------------

    def _narrate(self, node):
        Dialogue.say(node.text)

    def _decide(self, hero, node):
        """
        Offer only the choices whose flag conditions are met (Tasks 1, 2). A
        single available choice reads as 'press Enter to continue'; several is a menu.
        """
        offered = [c for c in node.choices if c.condition is None or c.condition(hero)]
        if not offered:
            offered = node.choices            # never soft-lock: fall back to all

        if len(offered) == 1:
            only = offered[0]
            console.print(f"[grey54]— {only.label} —[/grey54]", justify="center")
            Dialogue.press_enter()
            return only

        labels = {index: choice.label for index, choice in enumerate(offered)}
        index = Dialogue.choose("What do you do?", list(labels.keys()), labels=labels)
        return offered[index]

    def _apply(self, hero, choice):
        if choice.honor_change:
            hero.adjust_honor(choice.honor_change)
        if choice.wanted_change:
            hero.adjust_wanted(choice.wanted_change)
        if choice.effect is not None:
            choice.effect(hero)
        self._feedback(choice)

    def _feedback(self, choice):
        """Show the reputation shift so the player feels the weight of a choice."""
        parts = []
        if choice.honor_change:
            color = "green" if choice.honor_change > 0 else "red"
            parts.append(f"[{color}]Honor {choice.honor_change:+d}[/{color}]")
        if choice.wanted_change:
            color = "red" if choice.wanted_change > 0 else "green"
            parts.append(f"[{color}]Wanted {choice.wanted_change:+d}[/{color}]")
        if parts:
            console.print("   " + "     ".join(parts), justify="center")
            Dialogue.pause(0.6)
