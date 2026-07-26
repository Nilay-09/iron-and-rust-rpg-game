STARTING_TOWN = "dust_creek"
TOWNS = {
    "dust_creek": {
        "name": "Dust Creek",
        "description": (
            "A quiet farming settlement surrounded by dry fields and wooden ranches. "
            "The people are honest but poor, and every sunset carries the smell of dust. "
            "Many travelers begin their journey here."
        ),
        "danger": 1,
        "art": "dust_creek",
        "shop": {
            "name": "Miller's General Store",
            "weapons": ["revolver"],
            "items": ["bandage", "whiskey"],
        },
    },

    "blackridge": {
        "name": "Blackridge",
        "description": (
            "A booming coal mining town where fortunes are made and lives are lost. "
            "Smoke pours from the mines day and night, while fights in the saloons are "
            "more common than church sermons."
        ),
        "danger": 3,
        "art": "blackridge",
        "shop": {
            "name": "The Powder Keg",
            "weapons": ["revolver", "shotgun"],
            "items": ["whiskey", "medkit"],
        },
    },

    "silver_crossing": {
        "name": "Silver Crossing",
        "description": (
            "A wealthy railroad town connecting the eastern cities to the frontier. "
            "Merchants, politicians, and railroad barons compete for influence while "
            "thieves quietly prey on newcomers."
        ),
        "danger": 2,
        "art": "silver_crossing",
        "shop": {
            "name": "Crossing Mercantile",
            "weapons": ["revolver", "rifle"],
            "items": ["bandage", "whiskey", "medkit", "tonic"],
        },
    },

    "dead_man_pass": {
        "name": "Dead Man's Pass",
        "description": (
            "A lawless canyon settlement built around abandoned mines and outlaw hideouts. "
            "No sheriff lasts long here, and every stranger is watched with a hand near "
            "their holster."
        ),
        "danger": 5,
        "art": "dead_man_pass",
        "shop": {
            "name": "Blind Pete's Trading Post",
            "weapons": ["rifle", "shotgun"],
            "items": ["whiskey", "tonic"],
        },
    },

    "iron_forge": {
        "name": "Iron Forge",
        "description": (
            "The industrial heart of the frontier. Massive foundries, blacksmiths, and "
            "factories fill the air with smoke and sparks. Here, iron is worth more than gold."
        ),
        "danger": 4,
        "art": "iron_forge",
        "shop": {
            "name": "Forge & Iron Armory",
            "weapons": ["revolver", "rifle", "shotgun"],
            "items": ["medkit", "tonic"],
        },
    },

    "redemption": {
        "name": "Redemption",
        "description": (
            "An isolated mountain town where people come to disappear from their past. "
            "Some seek peace, others hide terrible secrets. Every smile hides a story."
        ),
        "danger": 2,
        "art": "redemption",
        "shop": {
            "name": "The Quiet Hand",
            "weapons": ["revolver"],
            "items": ["bandage", "medkit", "tonic"],
        },
    }
}
