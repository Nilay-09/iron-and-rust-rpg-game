from iron_rust.world.world_map import WorldMap

world = WorldMap()

# Beginner Area
world.add_route("dust_creek", "silver_crossing", 2)
world.add_route("dust_creek", "blackridge", 3)

# Mid Game
world.add_route("silver_crossing", "iron_forge", 4)
world.add_route("blackridge", "iron_forge", 2)
world.add_route("blackridge", "dead_man_pass", 5)

# Late Game
world.add_route("iron_forge", "redemption", 3)
world.add_route("dead_man_pass", "redemption", 2)

# Optional hidden shortcut
world.add_route("silver_crossing", "redemption", 6)