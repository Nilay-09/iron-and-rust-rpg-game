from iron_rust.core.save_manager import has_save, load_game, save_game
from iron_rust.data.archetypes import ARCHETYPES
from iron_rust.data.genders import GENDERS
from iron_rust.data.roles import ROLES
from iron_rust.data.dialogues import DIALOGUES
from iron_rust.entities.hero import Hero
from iron_rust.quests import main_story
from iron_rust.ui.dialogue import Dialogue
from iron_rust.ui.intro import game_intro
from iron_rust.world.travel import travel_menu
from iron_rust.world.routes import world


class Game:
    def start(self):
        # Task 18: offer to continue a saved game on startup.
        if has_save():
            choice = Dialogue.choose(
                "A saved trail was found.",
                ["continue", "new"],
                labels={"continue": "Continue your saved game", "new": "Start a new game"},
            )
            if choice == "continue":
                hero = None
                try:
                    hero = load_game()
                except Exception:
                    hero = None
                if hero is not None:
                    Dialogue.success(f"Welcome back, {hero.name}.")
                    hero.show_sheet()
                    travel_menu(hero, world, Dialogue)
                    return
                Dialogue.narrator("That save was unreadable. Starting fresh.")

        self.character_creation()

    def create_hero(self, name, age, gender, role, archetype):
        return Hero(
            name=name,
            age=age,
            gender=gender,
            role=role,
            archetype=archetype,
        )

    def character_creation(self):
        game_intro()

        Dialogue.narrator(DIALOGUES["intro"]["wind"])
        Dialogue.pause()

        Dialogue.narrator(DIALOGUES["intro"]["old_man_steps_out"])
        Dialogue.pause()

        Dialogue.say(DIALOGUES["intro"]["greeting"])

        user_name = Dialogue.ask(DIALOGUES["intro"]["ask_name"])

        Dialogue.pause()

        Dialogue.say(DIALOGUES["intro"]["name_echo"].format(user_name=user_name))
        Dialogue.say(DIALOGUES["intro"]["name_remembered"])

        user_age = Dialogue.ask_int(DIALOGUES["intro"]["ask_age"])

        Dialogue.pause()

        Dialogue.say(DIALOGUES["intro"]["good"])
        Dialogue.say(DIALOGUES["intro"]["old_enough"])

        Dialogue.panel(
            DIALOGUES["intro"]["panel_identity_title"],
            DIALOGUES["intro"]["panel_identity_text"],
        )

        user_gender = Dialogue.choose(
            DIALOGUES["intro"]["ask_gender"],
            list(GENDERS.keys()),
            labels=GENDERS,
        )

        Dialogue.success(
            DIALOGUES["intro"]["gender_success"].format(gender=GENDERS[user_gender])
        )

        Dialogue.panel(
            DIALOGUES["intro"]["panel_occupation_title"],
            DIALOGUES["intro"]["panel_occupation_text"],
        )

        role_labels = {
            role: role.title()
            for role in ROLES
        }

        user_role = Dialogue.choose(
            DIALOGUES["intro"]["ask_role"],
            list(ROLES.keys()),
            labels=role_labels,
        )

        Dialogue.say(
            DIALOGUES["intro"]["role_reaction"].format(role=user_role.title())
        )

        Dialogue.pause()

        Dialogue.panel(
            DIALOGUES["intro"]["panel_soul_title"],
            DIALOGUES["intro"]["panel_soul_text"],
        )

        archetype_labels = {
            archetype: archetype.replace("_", " ").title()
            for archetype in ARCHETYPES
        }

        user_archetype = Dialogue.choose(
            DIALOGUES["intro"]["ask_archetype"],
            list(ARCHETYPES.keys()),
            labels=archetype_labels,
        )

        Dialogue.say(DIALOGUES["intro"]["frontier_chosen"])

        Dialogue.pause()

        Dialogue.panel(
            DIALOGUES["intro"]["panel_legend_title"],
            DIALOGUES["intro"]["panel_legend_text"],
        )

        hero = self.create_hero(
            user_name,
            user_age,
            user_gender,
            user_role,
            user_archetype,
        )

        Dialogue.success(DIALOGUES["intro"]["character_created"])
        Dialogue.pause(1)
        hero.show_sheet()

        # Act 1: play out the opening betrayal before the world opens up.
        main_story.the_fall.play(hero)

        save_game(hero)          # Task 18: first save once the hero exists

        # Offer immediate travel after character creation
        travel_menu(hero, world, Dialogue)
