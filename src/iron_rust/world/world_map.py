class WorldMap:
    """
    The frontier as a weighted graph: towns are nodes, roads are undirected
    edges whose weight is travel time in hours. Stored as an adjacency list
    ({town: {neighbor: cost}}) and consumed by the pathfinding (BFS reachability
    and Dijkstra shortest paths), player travel, and the active pursuit.
    """

    def __init__(self):
        # Adjacency list:
        # {
        #   "dust_creek": {
        #       "blackridge": 2,
        #       "silver_crossing": 3
        #   }
        # }
        self.graph = {}

    def add_town(self, town_name):
        """Add a town to the map."""
        if town_name not in self.graph:
            self.graph[town_name] = {}

    def add_route(self, town_a, town_b, travel_cost):
        """
        Connect two towns.

        Example:
        Dust Creek <--2--> Blackridge
        """

        self.add_town(town_a)
        self.add_town(town_b)

        self.graph[town_a][town_b] = travel_cost
        self.graph[town_b][town_a] = travel_cost

    def neighbors(self, town_name):
        """Return all directly connected towns."""
        return self.graph.get(town_name, {})

    def towns(self):
        """Return every town on the map."""
        return list(self.graph.keys())