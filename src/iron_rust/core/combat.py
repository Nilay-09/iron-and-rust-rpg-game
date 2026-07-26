"""
Combat & Dead Eye duels.

Turn order is a collections.deque: participants are popped from the front to
act and pushed to the back if they survive. Stats matter here — luck grants
crits, intelligence fills Dead Eye faster, stealth powers the flee attempt —
and the hero can spend a turn on an item instead of a shot.
"""

import heapq
import random
from collections import deque

from iron_rust.core.status import add_status, status_value, tick_statuses
from iron_rust.ui.dialogue import Dialogue, console

# Called-shot effects for Dead Eye (Task 7).
CALLED_SHOTS = {
    "head": "Head — a killing shot",
    "arm": "Arm — disarm, weakens their attack",
    "leg": "Leg — cripple, they lose their next turn",
}

DEADEYE_GAIN = 30    # base Dead Eye filled per turn survived (+ intelligence)
HIT_TARGET = 15      # d20 + aim must meet/beat this to land a shot
DEADEYE_MULT = 1.5   # Dead Eye shots hit for this much of weapon damage
HERO_MAX_HP = 100    # ceiling for healing


class Combat:
    def __init__(self, hero, enemies, allies=None):
        self.hero = hero
        self.enemies = list(enemies)
        self.allies = list(allies) if allies else []   # gang backup (Milestone 5)
        self.order = deque()
        self.fled = False
        self.last_deadeye_targets = []   # exposed for inspection/tests

    def _living_allies(self):
        return [a for a in self.allies if getattr(a, "hp", 0) > 0]

    def _living_enemies(self):
        return [e for e in self.enemies if e.hp > 0]

    def _build_order(self):
        """Turn order deque: hero, then gang backup, then foes."""
        return deque([self.hero, *self._living_allies(), *self._living_enemies()])

    # -- targeting -----------------------------------------------------------

    @staticmethod
    def rank_targets(enemies):
        """Rank living enemies most-dangerous-first by threat_level, via heapq."""
        alive = [e for e in enemies if e.hp > 0]
        return heapq.nlargest(len(alive), alive, key=lambda e: e.threat_level)

    # -- rolls & stat effects ------------------------------------------------

    @staticmethod
    def _roll_hit(aim):
        return random.randint(1, 20) + aim >= HIT_TARGET

    def _hero_aim(self):
        return self.hero.stat("aim") + self.hero.equipped_weapon.get("accuracy", 0)

    def _weapon_damage(self):
        low, high = self.hero.equipped_weapon.get("damage", (5, 9))
        return random.randint(low, high)

    def _apply_luck_crit(self, dmg):
        """Task 3: luck grants a small chance to double damage (Silas's arc boosts it)."""
        chance = self.hero.stat("luck") / 100
        if self.hero.has_bonus("crit_up"):
            chance += 0.10
        if random.random() < chance:
            return dmg * 2, True
        return dmg, False

    def _deadeye_gain(self):
        """Task 4: intelligence increases how fast Dead Eye fills."""
        return DEADEYE_GAIN + self.hero.stat("intelligence") // 4

    # -- main loop -----------------------------------------------------------

    def run(self):
        """Fight until the hero drops, flees, or every enemy is dead."""
        # Clear any leftover statuses so nothing carries over between fights.
        if hasattr(self.hero, "statuses"):
            self.hero.statuses.clear()
        for e in self.enemies:
            if hasattr(e, "statuses"):
                e.statuses.clear()

        self._intro()
        self.order = self._build_order()
        self.fled = False

        while self.hero.hp > 0 and self._living_enemies() and not self.fled:
            actor = self.order.popleft()
            if actor.hp <= 0:
                continue                                   # fell earlier this round

            # Task 8: status effects tick at the start of the turn.
            skip = self._tick(actor)
            if actor.hp <= 0:
                self._say(f"{self._name(actor)} bleeds out.", "red")
                continue                                   # died to bleed; drop them
            if skip:
                if actor.hp > 0:
                    self.order.append(actor)               # stunned: lose the turn
                continue

            if actor is self.hero:
                self._hero_turn()
                if self.fled:
                    break
                if self.hero.hp > 0:
                    self.hero.gain_deadeye(self._deadeye_gain())
            elif actor in self.allies:
                self._ally_turn(actor)
            else:
                self._enemy_turn(actor)

            if actor.hp > 0:
                self.order.append(actor)                   # back of the line

        if self.fled:
            result = "fled"
        else:
            result = "victory" if self.hero.hp > 0 else "defeat"
        self._outro(result)
        return result

    # -- the hero's turn -----------------------------------------------------

    def _hero_turn(self):
        alive = self._living_enemies()
        action = self._choose_action()

        if action == "deadeye":
            self._deadeye(alive)
        elif action == "item":
            self._use_item_turn()
        elif action == "flee":
            self._attempt_flee()
        else:
            self._resolve_hero_shot(self._choose_target(alive))

    def _choose_action(self):
        options, labels = [], {}
        if self.hero.deadeye_ready:
            options.append("deadeye")
            labels["deadeye"] = "Trigger DEAD EYE — mark multiple targets"
        options.append("shot")
        labels["shot"] = "Take a shot"
        if self.hero.has_items():
            options.append("item")
            labels["item"] = "Use an item"
        options.append("flee")
        labels["flee"] = "Try to flee"
        return Dialogue.choose("Your move?", options, labels=labels)

    def _choose_target(self, alive):
        if len(alive) == 1:
            return alive[0]
        labels = {
            i: f"{e.name}  ({e.hp} HP, threat {e.threat_level})"
            for i, e in enumerate(alive)
        }
        index = Dialogue.choose("Take aim at...", list(labels.keys()), labels=labels)
        return alive[index]

    def _resolve_hero_shot(self, target):
        if self._roll_hit(self._hero_aim()):
            dmg, crit = self._apply_luck_crit(self._weapon_damage())
            target.hp = max(0, target.hp - dmg)
            crit_tag = " [bold]CRIT![/bold]" if crit else ""
            self._say(f"You fire — {target.name} takes {dmg} damage.{crit_tag}", "yellow")
            if target.hp <= 0:
                self._say(f"{target.name} drops.", "green")
        else:
            self._say(f"Your shot goes wide of {target.name}.", "grey62")

    def _use_item_turn(self):
        keys = [k for k, c in self.hero.consumables.items() if c > 0]
        from iron_rust.data.items import ITEMS
        labels = {k: f"{ITEMS[k]['name']} x{self.hero.consumables[k]} — {ITEMS[k]['desc']}" for k in keys}
        key = Dialogue.choose("Use which item?", keys, labels=labels)
        result = self.hero.use_item(key)
        if result:
            self._say(result, "green")

    def _attempt_flee(self):
        """Task 13: flee success is stealth-based, not guaranteed."""
        chance = 0.30 + self.hero.stat("stealth") / 25
        if random.random() < chance:
            self.fled = True
            self._say("You break contact and vanish into the country.", "cyan")
        else:
            self._say("You can't shake them — no way clear.", "grey62")

    # -- Dead Eye ------------------------------------------------------------

    def _deadeye(self, alive):
        ranked = self.rank_targets(alive)          # heapq ranking
        self._say("Time slows. You paint your targets.", "magenta")

        tags = self._tag_targets(ranked)           # [(enemy, part), ...]
        self.last_deadeye_targets = [e for e, _ in tags]

        for enemy, part in tags:
            self._resolve_called_shot(enemy, part)

        self.hero.deadeye = 0

    def _resolve_called_shot(self, enemy, part):
        """Task 7: where you hit changes the effect, not just the damage."""
        base = int(self._weapon_damage() * DEADEYE_MULT)
        if part == "head":
            dmg, crit = self._apply_luck_crit(int(base * 1.3))
            enemy.hp = max(0, enemy.hp - dmg)
            add_status(enemy, "bleed", turns=2, value=4)
            crit_tag = " CRIT!" if crit else ""
            fell = "  — down!" if enemy.hp <= 0 else " (bleeding)"
            self._say(f"  Dead Eye HEAD → {enemy.name} for {dmg}{crit_tag}{fell}", "red")
        elif part == "arm":
            dmg = int(base * 0.6)
            enemy.hp = max(0, enemy.hp - dmg)
            add_status(enemy, "disarm", turns=2, value=max(3, enemy.attack // 2))
            self._say(f"  Dead Eye ARM → {enemy.name} for {dmg} — disarmed!", "red")
        else:  # leg
            dmg = int(base * 0.6)
            enemy.hp = max(0, enemy.hp - dmg)
            add_status(enemy, "stun", turns=1, value=0)
            self._say(f"  Dead Eye LEG → {enemy.name} for {dmg} — crippled!", "red")

    def _tag_targets(self, ranked):
        """Tag up to 3 ranked targets (min 1), choosing a body part for each."""
        tags = []
        remaining = list(ranked)
        max_tags = 4 if self.hero.has_bonus("deadeye_slot") else 3   # Kate's arc
        limit = min(max_tags, len(remaining))

        while remaining and len(tags) < limit:
            labels = {
                i: f"{e.name}  (threat {e.threat_level}, {e.hp} HP)"
                for i, e in enumerate(remaining)
            }
            options = list(labels.keys())
            if len(tags) >= 2:                      # 2 tagged -> may fire early
                options.append(-1)
                labels[-1] = "Fire the combo now"

            pick = Dialogue.choose(
                f"Tag target {len(tags) + 1} of up to {limit}",
                options,
                labels=labels,
            )
            if pick == -1:
                break

            enemy = remaining.pop(pick)
            part = Dialogue.choose(
                f"Called shot on {enemy.name} — where?",
                list(CALLED_SHOTS.keys()),
                labels=CALLED_SHOTS,
            )
            tags.append((enemy, part))

        return tags

    # -- a gang ally's turn --------------------------------------------------

    def _ally_turn(self, ally):
        """
        Gang backup acts each round, dispatching on its `special` ability.
        Enemies still focus the hero, so allies are pure upside.
        """
        special = getattr(ally, "special", None)
        role = getattr(ally, "role", "").lower()

        if special == "field_medic" or "medic" in role:
            self._ally_heal(ally)
        elif special == "dynamite":
            self._ally_dynamite(ally)
        elif special == "sharpshooter":
            self._ally_sharpshot(ally)
        else:  # cover_fire / default
            self._ally_fire(ally)

    def _ally_heal(self, ally):
        loyalty = getattr(ally, "loyalty", 50)
        before = self.hero.hp
        self.hero.hp = min(HERO_MAX_HP, self.hero.hp + 8 + loyalty // 20)
        self._say(f"{ally.name} patches you up (+{self.hero.hp - before} HP).", "green")

    def _ally_bonus(self):
        """Camp Gunsmith upgrade and Eli's arc sharpen the whole gang."""
        bonus = 0
        gang = getattr(self.hero, "gang", None)
        if gang is not None and gang.has_upgrade("gunsmith"):
            bonus += 3
        if self.hero.has_bonus("ally_damage"):
            bonus += 2
        return bonus

    def _ally_fire(self, ally):
        loyalty = getattr(ally, "loyalty", 50)
        if self._roll_hit(6 + loyalty // 20):
            target = self.rank_targets(self._living_enemies())[0]
            dmg = max(1, 7 + loyalty // 20 + self._ally_bonus() + random.randint(-2, 2))
            target.hp = max(0, target.hp - dmg)
            fell = "  — down!" if target.hp <= 0 else ""
            self._say(f"{ally.name} fires — {target.name} takes {dmg}{fell}.", "cyan")
        else:
            self._say(f"{ally.name}'s shot misses.", "grey62")

    def _ally_dynamite(self, ally):
        """Special: hits every living enemy for a little damage."""
        targets = self._living_enemies()
        self._say(f"{ally.name} lights a stick and throws!", "orange1")
        for e in targets:
            e.hp = max(0, e.hp - (random.randint(5, 9) + self._ally_bonus()))
            if e.hp <= 0:
                self._say(f"  {e.name} is caught in the blast — down!", "red")

    def _ally_sharpshot(self, ally):
        """Special: a guaranteed high-damage hit on the worst threat."""
        target = self.rank_targets(self._living_enemies())[0]
        dmg = random.randint(14, 20) + self._ally_bonus()
        target.hp = max(0, target.hp - dmg)
        fell = "  — down!" if target.hp <= 0 else ""
        self._say(f"{ally.name} lines up a perfect shot — {target.name} takes {dmg}{fell}.", "cyan")

    # -- the enemy's turn ----------------------------------------------------

    def _enemy_turn(self, enemy):
        if self._roll_hit(enemy.aim):
            # Task 7/8: a disarmed enemy hits for less.
            base = enemy.attack - status_value(enemy, "disarm")
            dmg = max(1, base + random.randint(-2, 2))
            self.hero.hp = max(0, self.hero.hp - dmg)
            self._say(f"{enemy.name} hits you for {dmg}.", "red")
        else:
            self._say(f"{enemy.name} misses.", "grey62")

    # -- status ticking ------------------------------------------------------

    def _name(self, actor):
        return "You" if actor is self.hero else getattr(actor, "name", "?")

    def _tick(self, actor):
        """Apply an actor's statuses at turn start. Returns True if they skip."""
        if not hasattr(actor, "statuses"):
            return False
        messages, skip = tick_statuses(actor)
        for m in messages:
            color = "red" if "bleed" in m else "grey62"
            self._say(f"{self._name(actor)} {m}.", color)
        return skip

    # -- presentation --------------------------------------------------------

    def _say(self, text, style="white"):
        console.print(f"[{style}]{text}[/{style}]", justify="center")

    def _status(self):
        hp = self.hero.hp
        de = self.hero.deadeye
        filled = max(0, min(10, de * 10 // max(1, self.hero.DEADEYE_MAX)))
        de_bar = f"[magenta]{'#' * filled}[/magenta][grey30]{'-' * (10 - filled)}[/grey30]"
        foes = "   ".join(
            f"[red]{e.name} {e.hp}HP[/red]" if e.hp > 0 else f"[grey42]{e.name} down[/grey42]"
            for e in self.enemies
        )
        console.print(
            f"[green]You {hp}HP[/green]   Dead Eye {de_bar}   [grey54]vs[/grey54]   {foes}",
            justify="center",
        )

    def _intro(self):
        names = ", ".join(e.name for e in self.enemies)
        console.print()
        self._say(f"— DUEL: {names} —", "bold red")
        for ally in self._living_allies():
            self._say(f"{ally.name} ({ally.role}) rides in at your side.", "cyan")
        self._status()

    def _outro(self, result):
        if result == "victory":
            self._say("The last of them falls. You are still standing.", "bold green")
        elif result == "fled":
            self._say("You live to ride another day.", "cyan")
        else:
            self._say("Your gun goes silent. The dust takes you.", "bold red")


def start_duel(hero, enemies, allies=None):
    """
    Convenience entry point. `enemies` may be a single Enemy or a list; `allies`
    is optional gang backup. Returns 'victory', 'defeat', or 'fled'.
    """
    if not isinstance(enemies, (list, tuple)):
        enemies = [enemies]
    return Combat(hero, list(enemies), allies=allies).run()
