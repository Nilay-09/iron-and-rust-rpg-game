from collections import deque
import heapq


def can_reach(world, start, destination):
    """
    Check whether a destination can be reached from the start town
    using Breadth-First Search (BFS).

    Returns:
        True  -> Destination is reachable
        False -> Destination is not reachable
    """

    # Invalid towns
    if start not in world.graph or destination not in world.graph:
        return False

    visited = set()
    queue = deque([start])

    while queue:
        current = queue.popleft()

        if current == destination:
            return True

        if current in visited:
            continue

        visited.add(current)

        for neighbor in world.neighbors(current):
            if neighbor not in visited:
                queue.append(neighbor)

    return False


def shortest_path(world, start, destination):
    """
    Find the shortest path using Dijkstra's Algorithm.

    Returns:
        (path, total_cost)

    Example:
        (['dust_creek', 'silver_crossing', 'iron_forge'], 6)

    If unreachable:
        (None, float('inf'))
    """

    # First check if destination is reachable
    if not can_reach(world, start, destination):
        return None, float("inf")

    # (cost, current_town, path_taken)
    priority_queue = [(0, start, [])]

    visited = set()

    while priority_queue:

        current_cost, current_town, current_path = heapq.heappop(priority_queue)

        if current_town in visited:
            continue

        visited.add(current_town)

        current_path = current_path + [current_town]

        if current_town == destination:
            return current_path, current_cost

        for neighbor, travel_cost in world.neighbors(current_town).items():

            if neighbor not in visited:

                heapq.heappush(
                    priority_queue,
                    (
                        current_cost + travel_cost,
                        neighbor,
                        current_path,
                    ),
                )

    return None, float("inf")