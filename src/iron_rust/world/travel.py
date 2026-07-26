import random
from time import sleep

from rich import box
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table

from rich.panel import Panel

from iron_rust.core.camp import camp_menu
from iron_rust.core.combat import start_duel
from iron_rust.core.pursuit import (
    advance_pursuer, clear_pursuer, gives_up, should_spawn, spawn_pursuer,
)
from iron_rust.core.save_manager import save_game
from iron_rust.core.shop import shop_menu
from iron_rust.data.enemies import spawn, spawn_for_danger
from iron_rust.data.towns import STARTING_TOWN, TOWNS
from iron_rust.quests.act2 import maybe_lawman, maybe_preacher
from iron_rust.quests.main_story import play_act3, the_crossroads
from iron_rust.quests.side_quests import (
    the_field_medic, the_powder_run, the_reunion, the_stagecoach,
)
from iron_rust.ui.dialogue import console
from iron_rust.utils.ascii_art import load_art
from iron_rust.world.pathfinding import shortest_path

# Optional story encounters that can surface mid-journey. Each fires at most
# once, moving honor / money / gang so the player's Act 3 ending is earned.
OPTIONAL_ENCOUNTERS = [
    ("crossroads", the_crossroads),
    ("reunion", the_reunion),
    ("stagecoach", the_stagecoach),
    ("field_medic", the_field_medic),
    ("powder_run", the_powder_run),
]
ENCOUNTER_CHANCE = 0.35

# The hero's home base — the only town with a gang camp to return to.
HOME_BASE = STARTING_TOWN

# Task 6: morale slips this much each ride the player doesn't tend the camp.
MORALE_DECAY = 3

# Task 5: Act 3 unlocks once the hero has seen this many towns.
ACT3_TOWNS_REQUIRED = 3

# Danger rating -> (word, Rich color). Used to color the destinations board.
DANGER_LABELS = {
    1: ("Calm", "green"),
    2: ("Uneasy", "chartreuse3"),
    3: ("Rough", "yellow"),
    4: ("Dangerous", "dark_orange"),
    5: ("Deadly", "red"),
}


def _line(text, style="italic grey62"):
    """Print one centered line of scene flavor, instantly (no animation)."""
    console.print(f"[{style}]{text}[/{style}]", justify="center")


def _scene(text, style="italic grey62", speed=0.012):
    """
    Reveal one centered line letter by letter, in place — a cinematic typewriter.
    The line is pre-centered so it types where the finished line will sit, rather
    than crawling out from the middle.
    """
    pad = max(0, (console.width - len(text)) // 2)
    if pad:
        console.print(" " * pad, end="")
    for ch in text:
        console.print(ch, end="", style=style, markup=False, highlight=False)
        sleep(speed)
    console.print()

# ----------------------------------------------------------------------
# Flavor tables — drawn from at random to keep every ride feeling new.
# ----------------------------------------------------------------------

WEATHER = [
    ("a hard sun overhead", "yellow"),
    ("a sky the color of old iron", "grey70"),
    ("a dry wind kicking up the dust", "khaki1"),
    ("rain coming in sideways", "steel_blue1"),
    ("a cold that settles in the bones", "light_steel_blue"),
    ("heat shimmering off the trail", "orange1"),
]

TIME_OF_DAY = [
    "first light",
    "high noon",
    "the long shadows of late afternoon",
    "dusk",
    "the blue dark after sundown",
]

# Atmospheric beats shown mid-ride. Purely for mood.
TRAIL_SIGHTS = [
    "A vulture wheels overhead, patient and unhurried.",
    "The bleached bones of some old beast mark the roadside.",
    "Somewhere off in the brush, a coyote calls and goes quiet.",
    "A broken wagon rots where its owners left it.",
    "Telegraph poles march off toward the horizon, humming faintly.",
    "The trail narrows between two walls of red rock.",
    "You pass a lonely grave with no name cut into the wood.",
]


# Danger-scaled encounters. Each may nudge the hero a little.
# effect(hero) -> short line describing the outcome, or None for pure flavor.
def _find_coin(hero):
    hero.money += 5
    return "You dig it free of the dirt. Five dollars richer for the stooping."


def _bandit_toll(hero):
    loss = min(getattr(hero, "money", 0), 10)
    hero.money -= loss
    return f"You pay the toll rather than the price of arguing. -${loss}."


def _hard_miles(hero):
    hero.hp = max(1, hero.hp - 5)
    return "The country takes its due. You ride on, saddle-sore. -5 HP."


TRAIL_EVENTS = [
    # (min_danger, weight, narration, effect_or_None)
    (1, 6, "The miles pass without trouble. Small mercy out here.", None),
    (1, 2, "A glint in the roadbed catches your eye - a coin, half-buried.", _find_coin),
    (2, 3, "Riders watch you from a far ridgeline, then melt away.", None),
    (3, 3, "Two men step from the rocks with rifles and reasonable smiles.", _bandit_toll),
    (3, 2, "The trail turns to broken shale and switchbacks.", _hard_miles),
    (4, 2, "Gunsmoke drifts on the wind from somewhere ahead. You give it a wide berth.", None),
    (5, 2, "A body swings from a lone tree at the crossroads. You do not linger.", None),
]

# ----------------------------------------------------------------------
# Camp — a long road is broken by a night under the stars.
# ----------------------------------------------------------------------

# Roads this long or longer force an overnight camp.
CAMP_THRESHOLD = 4

# The hero's HP ceiling. Rest never pushes past this.
MAX_HP = 100

# Shown while making camp, before the fire/cold choice — no fire assumed yet.
CAMP_SETUP_LINES = [
    "You lead the horse off the trail and unsaddle in the failing light.",
    "You find a hollow out of the wind and lay down your gear.",
    "The horse is watered, hobbled, and left to crop the thin grass.",
    "You clear a patch of hard ground and settle in against the dark.",
    "The saddle comes off; the day's dust comes with it.",
]

# Shown only if the player chooses to build a fire.
CAMPFIRE_LINES = [
    "You gather deadwood and coax a fire out of the dark.",
    "Coffee boils in a dented tin. The horse cools beside you.",
    "Flames throw long shadows against the rocks. The night breathes.",
    "Sparks climb toward a sky thick with cold, indifferent stars.",
]


def _watchful_night(hero):
    # Kept your gun close; a prowler thinks better of it.
    return "You wake once to snapping brush, hand already on iron. Nothing comes."


def _prowler(hero):
    loss = min(getattr(hero, "money", 0), 8)
    hero.money -= loss
    return f"By morning a saddlebag hangs open. Something got past you. -${loss}."


def _night_ambush(hero):
    hero.hp = max(1, hero.hp - 12)
    return "Shapes rush the firelight. You fight clear, bleeding, and ride before dawn. -12 HP."


def _kind_stranger(hero):
    hero.hp = min(MAX_HP, hero.hp + 6)
    return "A drifter shares your fire and his tobacco. You sleep the better for company. +6 HP."


# effective danger = road danger, +1 if a fire was lit (a fire draws eyes).
NIGHT_EVENTS = [
    # (min_danger, weight, narration, effect_or_None)
    (1, 6, "The night passes quiet, but for the wind and the horse's slow breathing.", None),
    (1, 2, "Coyotes sing the dark away somewhere out past the edge of camp.", None),
    (2, 2, "A stranger's fire glows a mile off. Neither of you closes the distance.", None),
    (2, 2, "Footsteps circle the camp at the edge of the light.", _watchful_night),
    (3, 2, "You share the fire with a passing drifter who means no harm.", _kind_stranger),
    (4, 3, "You wake to hands in your gear and the dark swallowing a running figure.", _prowler),
    (5, 3, "The firelight brings the wrong kind of company.", _night_ambush),
]


def _danger_cell(level):
    """A colored danger bar + word for the Rich board (markup is fine here)."""
    level = max(1, min(5, int(level)))
    word, color = DANGER_LABELS[level]
    bar = f"[{color}]{'#' * level}[/{color}][grey30]{'-' * (5 - level)}[/grey30]"
    return f"{bar}  [{color}]{word}[/{color}]"


def _status_bar(hero):
    """A colored ribbon: who you are, how you're holding up, and your coin."""
    hp = getattr(hero, "hp", MAX_HP)
    money = getattr(hero, "money", 0)
    name = getattr(hero, "name", "Stranger")
    town = TOWNS.get(getattr(hero, "location", ""), {}).get("name", "the frontier")

    hp_color = "green" if hp > 60 else "yellow" if hp > 30 else "red"
    filled = max(0, min(10, hp // 10))
    hp_bar = f"[{hp_color}]{'#' * filled}[/{hp_color}][grey30]{'-' * (10 - filled)}[/grey30]"

    # Dead Eye meter — persists between fights, so the player watches it charge.
    de = getattr(hero, "deadeye", 0)
    de_max = getattr(hero, "DEADEYE_MAX", 100)
    if de >= de_max:
        deadeye = "[bold magenta]DEAD EYE READY[/bold magenta]"
    else:
        de_filled = max(0, min(10, de * 10 // max(1, de_max)))
        de_bar = f"[magenta]{'#' * de_filled}[/magenta][grey30]{'-' * (10 - de_filled)}[/grey30]"
        deadeye = f"[magenta]Dead Eye[/magenta] {de_bar}"

    dot = "[grey42] · [/grey42]"
    console.print(
        f"[bold khaki1]{name}[/bold khaki1]{dot}"
        f"HP {hp_bar} [{hp_color}]{hp}/{MAX_HP}[/{hp_color}]{dot}"
        f"{deadeye}{dot}"
        f"[gold1]Gold ${money}[/gold1]{dot}"
        f"[cyan]{town}[/cyan]",
        justify="center",
    )


def _show_board(current, neighbors, destinations):
    """A colored table of every road out of town — distance and danger at a glance."""
    table = Table(
        title=f"The roads out of {TOWNS[current]['name']}",
        title_style="bold khaki1",
        box=box.SIMPLE_HEAVY,
        border_style="grey37",
        padding=(0, 3),
        header_style="grey54",
    )
    table.add_column("Destination", style="bold")
    table.add_column("Ride", justify="right")
    table.add_column("Danger")

    for town in destinations:
        hours = neighbors[town]
        table.add_row(
            TOWNS[town]["name"],
            f"{hours}h",
            _danger_cell(TOWNS[town].get("danger", 1)),
        )

    console.print()
    console.print(table)
    console.print()


def _departure(dialogue, origin, destination, hours):
    """The moment of leaving - saddle up and ride out."""
    weather, w_style = random.choice(WEATHER)
    time_of_day = random.choice(TIME_OF_DAY)
    heading = random.choice(["north", "south", "east", "west"])

    dialogue.divider()
    console.print()
    _scene(
        f"You cinch the saddle, check the loads in your gun, "
        f"and turn your back on {TOWNS[origin]['name']}."
    )
    _scene(f"You ride out at {time_of_day}, {weather}.", w_style)
    _scene(f"{TOWNS[destination]['name']} lies {hours} hours to the {heading}.", "grey54")
    dialogue.pause(0.6)


def _ride(dialogue, destination, hours):
    """Animate the crossing with a smooth trail bar and one mid-ride sight."""
    steps = 60                         # fixed steps -> steady, even motion
    sight = random.choice(TRAIL_SIGHTS)
    name = TOWNS[destination]["name"]

    console.print()
    with Progress(
        TextColumn(f"[bold khaki1]On the trail to {name}[/bold khaki1]"),
        BarColumn(bar_width=44, complete_style="dark_orange3", finished_style="dark_orange3"),
        TextColumn("[grey54]{task.percentage:>3.0f}%[/grey54]"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("ride", total=steps)
        for step in range(steps):
            progress.advance(task)
            if step == steps // 2:
                _line(sight)           # instant: it prints over the live ride bar
            sleep(0.03)                # constant delay -> no stutter


def _maybe_story_encounter(hero, dialogue):
    """Chance to stumble into an unseen optional quest that shifts honor/gang."""
    seen = getattr(hero, "seen_encounters", None)
    if seen is None:
        return

    available = [(key, quest) for key, quest in OPTIONAL_ENCOUNTERS if key not in seen]
    if not available or random.random() > ENCOUNTER_CHANCE:
        return

    key, quest = random.choice(available)
    dialogue.divider()
    quest.play(hero)
    seen.add(key)
    dialogue.pause(0.6)


def _maybe_ambush(hero, dialogue, danger):
    """
    Chance of a trailside duel, scaled by danger. Stealth can slip it entirely
    (Task 1); charisma can talk it down (Task 2). Enemy strength scales with the
    road's danger (Task 14). On defeat the hero is beaten but alive.
    """
    chance = 0.10 + 0.06 * danger        # danger 1 ~16%, danger 5 ~40%
    if random.random() > chance:
        return

    enemies = spawn_for_danger(danger)   # Task 14: difficulty follows danger
    names = " and ".join(e.name for e in enemies)

    dialogue.divider()
    _scene(f"{names} move to block the trail ahead.", "red")

    # Task 1 — Stealth: a chance to avoid the fight entirely.
    stealth_chance = hero.stat("stealth") / 25
    if random.random() < stealth_chance:
        _scene("You read the ground early and slip off the trail unseen.", "cyan")
        dialogue.pause(0.6)
        return

    # Task 2 — Charisma: try to talk your way out instead of drawing.
    if hero.stat("charisma") >= 6:
        pick = dialogue.choose(
            "How do you play it?",
            ["talk", "draw"],
            labels={
                "talk": "Talk your way out of it (charisma)",
                "draw": "Draw and fight",
            },
        )
        if pick == "talk":
            if random.random() < 0.25 + hero.stat("charisma") / 20:
                _scene("You spin a story smooth enough that they wave you through.", "cyan")
                dialogue.pause(0.6)
                return
            _scene("They don't buy a word of it. Iron it is.", "grey70")

    # Task 4 payoff: backup joins on high morale OR strong gang standing.
    allies = _gang_allies(hero)
    if allies:
        _scene(f"{allies[0].name} rides up hard behind you.", "cyan")
    dialogue.pause(0.4)

    result = start_duel(hero, enemies, allies=allies)

    if result == "defeat":
        hero.hp = max(hero.hp, 20)                       # patched up, not dead
        loss = min(getattr(hero, "money", 0), 15)
        hero.money -= loss
        _scene(f"They leave you bleeding in the dirt, lighter by ${loss}.", "grey70")
    elif result == "fled":
        _scene("You put the miles between you and the guns.", "cyan")
    else:
        _scene("You holster a hot gun. The trail is yours again.", "khaki1")
    dialogue.pause(0.6)


def _trail_event(hero, dialogue, danger):
    """Roll a danger-scaled encounter and apply any effect."""
    candidates = [e for e in TRAIL_EVENTS if e[0] <= danger]
    weights = [e[1] for e in candidates]
    _, _, narration, effect = random.choices(candidates, weights=weights, k=1)[0]

    console.print()
    _scene(narration)
    if effect is not None:
        outcome = effect(hero)
        if outcome:
            _scene(outcome, "grey70")
            dialogue.pause(0.6)


def _rest(hero, amount):
    """Restore HP, capped at MAX_HP. Returns HP actually healed."""
    before = hero.hp
    hero.hp = min(MAX_HP, hero.hp + amount)
    return hero.hp - before


def _make_camp(hero, dialogue, danger):
    """
    An overnight camp on the long roads. The player chooses how to spend the
    night, trading rest against safety, then the dark rolls its own dice.
    """
    dialogue.divider()
    console.print()
    _scene("The light goes out of the sky and the road with it. You make camp.")
    _scene(random.choice(CAMP_SETUP_LINES))
    dialogue.pause(0.6)

    FIRE, COLD = "fire", "cold"
    choice = dialogue.choose(
        "How do you pass the night?",
        [FIRE, COLD],
        labels={
            FIRE: "Build a fire    warmth and real rest, but the light carries far",
            COLD: "Cold camp       no fire, gun in hand; less rest, fewer eyes",
        },
    )

    if choice == FIRE:
        _scene(random.choice(CAMPFIRE_LINES))
        healed = _rest(hero, 25)
        effective_danger = danger + 1          # a fire draws the wrong company
    else:
        healed = _rest(hero, 12)
        effective_danger = max(1, danger - 1)  # dark and watchful

    if healed:
        _scene(f"You rest. +{healed} HP.", "green")
        dialogue.pause(0.6)

    # The dark rolls its own dice.
    candidates = [e for e in NIGHT_EVENTS if e[0] <= effective_danger]
    weights = [e[1] for e in candidates]
    _, _, narration, effect = random.choices(candidates, weights=weights, k=1)[0]

    console.print()
    _scene(narration)
    if effect is not None:
        outcome = effect(hero)
        if outcome:
            _scene(outcome, "grey70")
            dialogue.pause(0.6)

    _scene("Dawn finds you saddled and moving. The trail waits.", "khaki1")
    dialogue.pause(0.6)


def _arrival(dialogue, hero, destination):
    """Frame the arrival like the end of a scene, with the town's ASCII art."""
    data = TOWNS[destination]
    dialogue.pause(0.5)
    dialogue.success(f"You reach {data['name']}.")

    art = load_art(data.get("art", destination))     # Task 7: ASCII art on arrival
    if art:
        console.print(art, style="grey62", markup=False, highlight=False)

    dialogue.panel(data["name"], data["description"])
    hero.location = destination

    # Act 2 — recurring characters greet the hero on arrival.
    maybe_lawman(hero, dialogue)
    maybe_preacher(hero, dialogue)


def _handle_pursuit(hero, world, dialogue):
    """
    Active pursuit (Tasks 5, 6). Uses Dijkstra to close the gap each trip; the
    hero evades by staying ahead or turns to confront.
    """
    if should_spawn(hero):
        p = spawn_pursuer(hero, world)
        dialogue.divider()
        _scene(f"Word's out. {p['name']} takes your trail from {TOWNS[p['position']]['name']}.", "red")
        dialogue.pause(0.6)
        return

    if hero.pursuer is None:
        return

    if gives_up(hero):
        _scene("The trail's gone cold behind you. The hunter turns back.", "cyan")
        dialogue.pause(0.6)
        return

    status = advance_pursuer(hero, world)
    if status is None:
        return

    if status["caught"]:
        p = hero.pursuer
        dialogue.divider()
        _scene(f"{p['name']} rides into town and steps down, hand near his gun.", "red")
        pick = dialogue.choose(
            "The hunter has run you to ground.",
            ["confront", "slip"],
            labels={"confront": "Turn and confront him", "slip": "Try to slip away (stealth)"},
        )
        if pick == "slip" and random.random() < 0.25 + hero.stat("stealth") / 25:
            _scene("You lose him in the crowd and are gone before he blinks.", "cyan")
            clear_pursuer(hero)          # escaped clean (a new hunter may pick up the trail later)
            dialogue.pause(0.6)
            return
        if pick == "slip":
            _scene("He's too close — no slipping this one.", "grey70")

        allies = _gang_allies(hero)
        result = start_duel(hero, spawn("bounty_hunter", name=p["name"]), allies=allies)
        if result == "victory":
            hero.adjust_wanted(-30)
            hero.adjust_faction("law", -10)
            clear_pursuer(hero)
            _scene("The hunter falls. The bounty on you cools considerably.", "khaki1")
        elif result == "defeat":
            hero.hp = max(hero.hp, 20)
            loss = min(getattr(hero, "money", 0), 40)
            hero.money -= loss
            hero.adjust_wanted(-15)
            clear_pursuer(hero)
            _scene(f"He beats you down and collects part of the bounty — ${loss} gone.", "grey70")
        else:  # fled the duel
            _scene("You break off and ride hard. He'll pick the trail back up.", "cyan")
        dialogue.pause(0.6)
    else:
        dist = status["distance"]
        _scene(f"{hero.pursuer['name']} is {dist} town{'s' if dist != 1 else ''} behind and closing.", "grey70")
        dialogue.pause(0.4)


def _gang_allies(hero):
    """Backup joins if morale is high OR gang faction standing is strong (Task 4)."""
    gang = getattr(hero, "gang", None)
    if gang is None or not gang.members:
        return []
    if gang.backup_ready or hero.faction("gang") >= 30:
        return [gang.best_backup()]
    return []


def _show_journal(hero, dialogue):
    """Quest journal (Task 11): active/completed quests with one-line status."""
    console.print()
    if not hero.journal:
        console.print("[grey54]Your journal is empty. Go make some history.[/grey54]", justify="center")
    else:
        lines = []
        for entry in hero.journal.values():
            done = entry["status"] == "completed"
            mark = "[green]✓[/green]" if done else "[yellow]•[/yellow]"
            style = "grey54" if done else "white"
            note = f" — [grey54]{entry['note']}[/grey54]" if entry.get("note") else ""
            lines.append(f"{mark} [{style}]{entry['title']}[/{style}] [grey42]({entry['status']})[/grey42]{note}")
        console.print(Panel("\n".join(lines), title="[bold]Journal[/bold]", border_style="grey37", padding=(1, 3)))
    dialogue.pause(0.4)
    try:
        console.input("")
    except EOFError:
        pass


def _rob_bank(hero, dialogue, town_key):
    """Dynamic economy (Task 9): rob the bank — quick money, lasting consequences."""
    town = TOWNS[town_key]
    if hero.has_flag(f"robbed_bank_{town_key}"):
        dialogue.narrator("You already cleaned out this bank. There's nothing left to take.")
        dialogue.pause(0.6)
        return

    haul = random.randint(120, 200)
    hero.money += haul
    hero.adjust_wanted(20)
    hero.adjust_honor(-10)
    hero.adjust_town_rep(town_key, -50)          # tanks local standing -> shop refuses
    hero.adjust_faction("law", -20)
    hero.set_flag(f"robbed_bank_{town_key}")
    hero.journal_add(f"bank_{town_key}", f"Robbed the bank in {town['name']}", "completed")

    dialogue.divider()
    _scene(f"You crack the {town['name']} bank and ride out ${haul} richer — and a "
           f"lot more wanted. This town won't forget.", "red")
    dialogue.pause(0.7)


def _travel_to(hero, world, dialogue, origin, destination):
    """Play one full journey between two towns, then apply its after-effects."""
    # shortest_path gives the true road cost even for a direct neighbor.
    path, cost = shortest_path(world, origin, destination)
    hours = cost if cost != float("inf") else world.neighbors(origin).get(destination, 3)
    danger = TOWNS[destination].get("danger", 1)

    _departure(dialogue, origin, destination, hours)   # Prepare horse
    _ride(dialogue, destination, hours)                 # Ride animation
    _trail_event(hero, dialogue, danger)               # Random encounter
    _maybe_story_encounter(hero, dialogue)             # Chance of an optional quest
    _maybe_ambush(hero, dialogue, danger)              # Chance of a duel (danger-scaled)
    if hours >= CAMP_THRESHOLD:                         # Camp (long roads only)
        _make_camp(hero, dialogue, danger)
    _arrival(dialogue, hero, destination)              # Arrive + ASCII + Act 2 NPCs
    _handle_pursuit(hero, world, dialogue)             # Tasks 5, 6: the law closes in

    if hasattr(hero, "visited_towns"):
        hero.visited_towns.add(destination)            # DSA: Set — unlocks Act 3

    # Task 6/17: neglecting the camp costs morale, and can cost you a member.
    gang = getattr(hero, "gang", None)
    if gang is not None and gang.members:
        decay = MORALE_DECAY - (1 if gang.has_upgrade("war_chest") else 0)
        gang.adjust_morale(-decay)
        deserter = gang.check_desertion()
        if deserter is not None:
            hero.gang_deserters += 1
            _scene(f"{deserter.name} has had enough of empty pockets and rides off in the night.", "red")
            dialogue.pause(0.6)

    save_game(hero)          # Task 18: autosave after every journey
    dialogue.pause(0.8)


def travel_menu(hero, world, dialogue):
    """
    Cinematic travel. Show the roads out of the current town - each with its
    distance and danger - then play the journey out as a scene: departure,
    the ride, a trail encounter, and arrival.
    """
    STAY = "__stay__"
    CAMP = "__camp__"
    FACE_PAST = "__face_past__"
    SHOP = "__shop__"
    GO_BACK = "__go_back__"
    JOURNAL = "__journal__"
    ROB = "__rob__"

    while True:
        current = hero.location
        here = TOWNS[current]

        neighbors = world.neighbors(current)
        if not neighbors:
            dialogue.clear()
            _status_bar(hero)
            _scene("There are no roads leading out of this town. The frontier ends here.")
            dialogue.pause(1)
            return

        # Order destinations by distance so the board reads naturally.
        destinations = sorted(neighbors.keys(), key=lambda t: neighbors[t])

        dialogue.clear()
        _status_bar(hero)                                   # who/HP/gold ribbon
        dialogue.panel(                                     # town intro
            f"{here['name']} - {random.choice(TIME_OF_DAY).title()}",
            here["description"],
        )
        _show_board(current, neighbors, destinations)       # colored roads board

        # The board carries the detail; the selector just needs the pick.
        labels = {t: f"Ride to {TOWNS[t]['name']}  ({neighbors[t]}h)" for t in destinations}

        options = list(destinations)

        # Task 5: every town with a shop lets you trade.
        if here.get("shop"):
            options.append(SHOP)
            labels[SHOP] = f"Visit {here['shop']['name']}"
            # Task 9: and a bank worth robbing (once).
            if not hero.has_flag(f"robbed_bank_{current}"):
                options.append(ROB)
                labels[ROB] = "Rob the bank (fast money, lasting heat)"

        # Task 11: the quest journal, always available.
        options.append(JOURNAL)
        labels[JOURNAL] = "Open your journal"

        # Task 7: the home-base town offers a way back to the gang camp.
        if current == HOME_BASE:
            options.append(CAMP)
            labels[CAMP] = "Return to Camp"

        # Task 21 (DSA: Stack): backtrack to the town you just came from.
        if hero.town_history:
            prev = hero.town_history[-1]
            options.append(GO_BACK)
            labels[GO_BACK] = f"Go back to {TOWNS[prev]['name']}"

        # Task 5 (Act 3): once the hero has seen enough of the frontier, it unlocks.
        if len(getattr(hero, "visited_towns", set())) >= ACT3_TOWNS_REQUIRED and not getattr(hero, "act3_done", False):
            options.append(FACE_PAST)
            labels[FACE_PAST] = "Face your past — hunt down the betrayer"

        options.append(STAY)
        labels[STAY] = "Rest here — save and quit"

        choice = dialogue.choose(
            "Which way do you ride?",
            options,
            labels=labels,
        )

        if choice == SHOP:
            shop_menu(hero, current, dialogue)
            save_game(hero)
            continue                      # back to the town screen

        if choice == ROB:
            _rob_bank(hero, dialogue, current)
            save_game(hero)
            continue

        if choice == JOURNAL:
            _show_journal(hero, dialogue)
            continue

        if choice == CAMP:
            camp_menu(hero, dialogue)
            save_game(hero)
            continue                      # back to the town screen

        if choice == GO_BACK:
            destination = hero.town_history.pop()   # DSA: Stack pop
            _travel_to(hero, world, dialogue, current, destination)
            continue

        if choice == FACE_PAST:
            ending = play_act3(hero)      # the Reckoning, the duel, the ending
            if ending is None:            # fled the final duel — reckoning postponed
                save_game(hero)
                continue                  # back to the world, the option remains
            hero.act3_done = True
            save_game(hero)
            return                        # the story is over

        if choice == STAY:
            save_game(hero)
            console.print()
            _scene("You bed down for the night. Your progress is saved — ride again soon.", "khaki1")
            dialogue.pause(0.8)
            return

        # A normal ride: push where we came from so we can backtrack later.
        hero.town_history.append(current)               # DSA: Stack push
        _travel_to(hero, world, dialogue, current, choice)
