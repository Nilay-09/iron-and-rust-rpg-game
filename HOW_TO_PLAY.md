# How to Play — Iron & Rust

New here? Read this once and you'll know everything you need. It takes about
two minutes.

---

## The story so far

You rode with an outlaw crew. On a payroll-train job, your partner **Rourke**
double-crossed everyone, shot you, took the gold, and left you for dead in the
dust. You wake up in a stranger's wagon — alive, broke, and alone.

**Your goal: track Rourke down and settle the score.** *How* you get there —
saint or devil, alone or with a loyal gang — decides how your story ends.

---

## Starting the game

Install it once with `pip install iron-and-rust`, then just run:

```
iron-rust
```

(Or `python -m iron_rust` if you prefer.)

If you've played before, you'll be asked to **Continue** or start **New**. The
game **saves automatically** after every trip, so you can quit any time and pick
up where you left off.

---

## Controls

- **Menus:** press **↑ / ↓** to move the `❯` pointer, **ENTER** to choose.
- **Typing:** when asked your name or age, just type and press ENTER.
- **Quit anytime:** press **Ctrl+C**, or choose **"Rest here — save and quit"**
  in a town. Either way your progress is saved.

That's it. The whole game is menus and typing — no twitch reflexes.

---

## Making your character

You'll pick a **name, age, gender, role, and archetype**. The archetype sets
your **stats**, and stats genuinely matter:

| Stat | What it does |
|------|--------------|
| **Aim** | How often your shots hit in a duel |
| **Luck** | Chance for a **critical hit** (double damage) |
| **Intelligence** | How fast your **Dead Eye** meter charges |
| **Stealth** | Chance to **avoid** an ambush or **flee** a fight |
| **Charisma** | Cheaper shops, and lets you **talk your way out** of some fights |

The **Gunslinger** (high aim + luck) is the easy pick for a first run. Others
lean on brains, charm, or stealth — all viable.

---

## The core loop

You spend the game in **towns**, choosing where to ride next. Each town menu
lets you:

- **Ride to a town** — the board shows each road's **travel time** and a
  **danger rating** (`#####` = deadly). Higher danger = tougher fights but
  better loot towns.
- **Visit the shop** — buy weapons and healing items, sell spare goods.
- **Rob the bank** — fast cash, but your **wanted** level spikes and that town
  turns on you (prices soar, then they stop serving you entirely).
- **Return to Camp** — only in your home base, **Dust Creek**. This is your gang
  HQ (see below).
- **Open your journal** — see which quests you've started and finished.
- **Face your past** — starts the **finale**. Appears once you've visited **3+
  towns**. Don't rush it (see "How to win").

On the road between towns you'll hit random events: scenery, **optional quests**
(help or rob people — each shifts your reputation), **ambushes** (duels), and on
long roads, an overnight **camp**.

---

## Duels (combat)

Fights are turn-based. On your turn you choose:

- **Take a shot** — your basic attack. Pick a target if there's more than one.
- **Trigger DEAD EYE** — only when the meter is **full**. Time slows: **tag up
  to 3 enemies** and, for each, pick where to hit:
  - **Head** — a killing shot (big damage + bleeding)
  - **Arm** — disarms them (they hit softer afterward)
  - **Leg** — cripples them (they lose their next turn)
- **Use an item** — heal up (Bandage / Whiskey / Medkit) or drink a **Tonic** to
  instantly charge Dead Eye.
- **Try to flee** — success depends on your **Stealth**. Not guaranteed.

**Bleeding** and **stun** tick at the start of a turn. **Luck** can crit any
shot. If you lose a road duel you're beaten but survive (patched up, lighter in
the pockets). Losing the **final** duel, though, is its own ending.

---

## Reputation — this is what shapes your ending

Two numbers follow you everywhere:

- **Honor** (−100 … +100): are you a good person or a bad one? Helping people
  raises it; robbing and betraying lowers it.
- **Wanted** (0 … 100): how badly the law wants you. Crimes raise it.

Once your **wanted** gets high, a **bounty hunter** starts chasing you across the
map — he moves one town closer every trip. **Evade** him by keeping on the move,
or **turn and confront** him. Beating him (or lowering your wanted) calls him
off.

There's also standing with the **Law**, your **Gang**, and each **town's
people** — helping the preacher doesn't make the sheriff trust you, and burning a
town's people makes its shop expensive (or closed).

**Low on honor?** Find **Father Ezekiel** in the quiet towns (Redemption, Dust
Creek) — he offers a redemption quest to climb back up.

---

## Your gang (the camp)

Return to **Camp** in Dust Creek to manage your crew:

- **Fund the pot** — move your money into the gang to raise **morale**.
- **High morale** → a gang member **rides into your duels as backup**.
- **Low morale** → members get fed up and **desert**.
- **Buy upgrades** — better gear (harder-hitting backup), a camp infirmary
  (heals you on arrival), a war chest (morale decays slower).
- **Sit with the gang** — play a member's **companion quest** for a **permanent
  bonus** (stronger backup, a shop discount, an extra Dead Eye target, or better
  crits).

Recruit members by choosing to *help* them in the road quests: **Eli** (The
Reunion), **Doc** (The Field Medic), **Kate** (The Powder Run).

---

## How to win

"Winning" = riding into the finale prepared, beating Rourke, and landing the
ending you want.

**Before you choose "Face your past":**
1. **Buy a better gun.** The starter pistol won't cut it against Rourke. Grab a
   Revolver, Rifle, or Shotgun from a shop.
2. **Stock healing items** (Medkits) — you can use them mid-duel.
3. **Build a gang** and **raise its morale to 60+** so a member fights beside you.
4. Do a **companion quest** or two for permanent bonuses.

Then choose **"Face your past."** Win the duel, make one final choice about
Rourke, and your ending is decided by your **honor, wanted, and gang**:

| Ending | How to get it |
|--------|---------------|
| **Redemption** | High **honor** (50+), low **wanted** (under 40). Play the good guy. |
| **Legend** | High **wanted** (55+), middling honor. Notorious, remembered in song. |
| **Hunted Down** | Low **honor** (−20 or worse) **and** high **wanted**. The villain's end. |
| **The Gang Leader** | Not extreme either way, but a **loyal gang** (a member, nobody deserted, morale 60+). |
| **Outlaw King** *(secret / best)* | **Honor 60+ AND Wanted 70+ AND a loyal gang** (morale 60+, no deserters). A beloved criminal with a kingdom at his back. |
| **Died With Your Boots On** | You **lose** the final duel. |

**Fastest "good" win:** keep honor high (help people, help the preacher), keep
wanted low (don't rob), buy a solid gun, and beat Rourke → **Redemption**.

**For the secret Outlaw King:** be *both* beloved and badly wanted — do honorable
deeds **and** commit crimes — while keeping a loyal, well-funded gang. The hardest
and most rewarding run.

---

## Quick tips

- **Don't rush the finale.** Explore, earn money, gear up, build the gang first.
- **Danger rating** on the travel board tells you how rough a road will be.
- **Charisma** pays off at every shop and can skip fights entirely.
- **Save Dead Eye** for when you're outnumbered — leg-shot the dangerous one to
  skip its turn, head-shot the rest.
- **Fund your camp regularly** — morale slips every trip you ignore it, and a
  deserting member can cost you the best ending.

Now saddle up, partner. The frontier's waiting.
