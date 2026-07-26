# 🤠 Iron & Rust

[![PyPI version](https://img.shields.io/pypi/v/iron-and-rust.svg?color=orange)](https://pypi.org/project/iron-and-rust/)
[![Python](https://img.shields.io/pypi/pyversions/iron-and-rust.svg)](https://pypi.org/project/iron-and-rust/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](https://pypi.org/project/iron-and-rust/)
[![Made with Rich](https://img.shields.io/badge/made%20with-Rich-red.svg)](https://github.com/Textualize/rich)

> **A Wild West RPG that runs in your terminal.** Ride a graph-based frontier,
> build a reputation the world actually remembers, and settle an old score with
> Dead Eye duels.

```text
██╗██████╗  ██████╗ ███╗   ██╗
██║██╔══██╗██╔═══██╗████╗  ██║
██║██████╔╝██║   ██║██╔██╗ ██║
██║██╔══██╗██║   ██║██║╚██╗██║
██║██║  ██║╚██████╔╝██║ ╚████║
╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
██████╗ ██╗   ██╗███████╗████████╗
██╔══██╗██║   ██║██╔════╝╚══██╔══╝
██████╔╝██║   ██║███████╗   ██║
██╔══██╗██║   ██║╚════██║   ██║
██║  ██║╚██████╔╝███████║   ██║
╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝
              A Terminal Western RPG
```

---

## Install & play

```bash
pip install iron-and-rust
```

```bash
iron-rust
```

That's it — no cloning, no scripts. Requires **Python 3.11+**. Works on Windows,
macOS, and Linux. Your progress **autosaves**; relaunch and pick **Continue**.

---

## The story

You rode with an outlaw crew. On a payroll-train job, your partner **Rourke**
double-crossed everyone — shot you, took the gold, and left you for dead in the
dust. You wake in a stranger's wagon with no crew, no money, and one thing left:
**a debt, and the long road it'll take to collect it.**

Ride the frontier. Help people or rob them. Gather a gang or ride alone. Every
choice bends toward one of **six endings** — and how you get there is the whole
point.

---

## What it looks like

The frontier is a map you navigate — each road has a distance and a danger rating:

```text
Cole · HP ########-- 80/100 · Dead Eye ######---- · Gold $142 · Silver Crossing

          The roads out of Silver Crossing

    Destination       Ride       Danger
 ───────────────────────────────────────────────────
    Dust Creek          2h       #----  Calm
    Iron Forge          4h       ####-  Dangerous
    Redemption          6h       ##---  Uneasy
```

Trouble on the trail becomes a Dead Eye duel:

```text
               — DUEL: Bandit, Rival Gunslinger —
   You 80HP   Dead Eye ######----   vs   Bandit 30HP · Gunslinger 40HP

   > Your move?
     > Trigger DEAD EYE — mark multiple targets
       Take a shot
       Use an item
       Try to flee
```

Fill the **Dead Eye** meter, then slow time and call your shots — **head** to
kill, **arm** to disarm, **leg** to cripple.

---

You rode with an outlaw crew. On a payroll-train job, your partner **Rourke**
double-crossed everyone — shot you, took the gold, and left you for dead in the
dust. You wake in a stranger's wagon with no crew, no money, and one thing left:
**a debt, and the long road it'll take to collect it.**

| Feature | What it means |
|---------|---------------|
| **Graph-based world** | Towns are nodes, roads are weighted edges. Travel runs on **Dijkstra's shortest path** — and so does the bounty hunter chasing you. |
| **The world remembers** | Not just two numbers — named story **flags**, independent **faction** standing, **per-NPC** relationships, and per-town reputation that moves shop prices. |
| **Dead Eye duels** | Turn-based combat with a chargeable meter, **called shots** (head / arm / leg), and status effects (bleed, stun). Your stats matter. |
| **Active pursuit** | Push your **wanted** level too high and a bounty hunter takes your trail, closing one town per trip. Outrun him or turn and fight. |
| **A gang to build** | Recruit members with unique combat specials, fund the camp, buy upgrades, and complete **companion arcs** for permanent bonuses. Neglect morale and they desert. |
| **A living economy** | Buy, sell, and rob. Burn a town's people and its shop marks you up — or refuses to serve you at all. |
| **Six endings** | Your final honor, wanted, gang, and one last moral choice over the betrayer decide how the story closes. |

---

## How the world works

Every action feeds two reputations that follow you everywhere:

- **Honor** (−100 … +100) — are you a good person, or a bad one?
- **Wanted** (0 … 100) — how badly the law wants you.

But the frontier tracks far more than that. A specific deed sets a **flag**, and
an NPC will reference it later ("that stagecoach driver described you real
well"). Helping the preacher raises *his* regard for you — not the marshal's.
Rob the bank in Blackridge and Blackridge remembers, even as the next town over
treats you fine.

Get too wanted and **Marshal Kane** escalates from a tip of the hat to a warning
to a duel — while a bounty hunter literally walks the map toward you.

Every stat pays off: **aim** lands shots, **luck** crits, **intelligence**
charges Dead Eye faster, **stealth** slips ambushes and powers your escape, and
**charisma** talks you out of fights and cuts shop prices.

---

## The six endings

| Ending | How you earn it |
|--------|-----------------|
| **Redemption** | High honor, low wanted. You made it right. |
| **Legend** | Notorious either way — remembered in a hundred saloons. |
| **Hunted Down** | Low honor **and** badly wanted. The law catches up. |
| **The Gang Leader** | Not extreme, but a loyal gang that never deserted you. |
| **Outlaw King** | *Secret.* Beloved **and** hunted, with a loyal gang at your back. |
| **Died With Your Boots On** | You lose the final duel. |

New here? [**HOW_TO_PLAY.md**](HOW_TO_PLAY.md) walks through every system and how
to reach each ending.

---

## Under the hood

Built from scratch in Python with [Rich](https://github.com/Textualize/rich) and
[InquirerPy](https://github.com/kazhala/InquirerPy) — and a deliberate tour of
data structures:

- **Graph + Dijkstra / BFS** for the world map, travel, and the closing pursuit
- **`deque`** for combat turn order, **`heapq`** for Dead Eye threat ranking
- **Sets** for visited towns and one-time events, a **stack** for backtracking
- A small **data-driven quest engine** (nodes + choices + flag conditions)
- Full **JSON save/load** of hero, gang, world memory, and quest journal

```text
src/iron_rust/
  core/       game loop, combat, camp, shop, pursuit, status, save_manager
  entities/   Hero, Enemy, NPC, Gang
  data/       towns, weapons, items, enemies, recruits, archetypes, roles
  quests/     quest engine, main story, side quests, Act 2, endings, companions
  world/      world_map, routes, pathfinding (Dijkstra/BFS), travel
  ui/         dialogue, intro
  assets/     per-town ASCII art
```

---

---

Per-user, outside the installed package:

| OS | Location |
|----|----------|
| Windows | `%LOCALAPPDATA%\IronAndRust\saves` |
| macOS | `~/Library/Application Support/IronAndRust/saves` |
| Linux | `$XDG_DATA_HOME/iron-and-rust/saves` |

---

---

## 💾 Where saves live

Per-user, outside the installed package:

| OS | Location |
|----|----------|
| Windows | `%LOCALAPPDATA%\IronAndRust\saves` |
| macOS | `~/Library/Application Support/IronAndRust/saves` |
| Linux | `$XDG_DATA_HOME/iron-and-rust/saves` |

---

## 🧑‍💻 Development

```bash
git clone https://github.com/Nilay-09/iron-and-rust-rpg-game.git
cd iron-and-rust-rpg-game
pip install -e .
python tests/run_all.py     # seven headless test suites
```

Building a release:

```bash
pip install build
python -m build             # -> dist/*.whl + *.tar.gz
```

---

## License

MIT — see [LICENSE](LICENSE). Built by **Nilay Bhotmange**.
