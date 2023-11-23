import heapq
import math


def aStar(graph, start, goal):
    # Initialize the open and closed sets
    open_set = [(0, start)]  # Priority queue of (f_score, node)
    closed_set = set()

    # Initialize dictionaries to store g_scores and parents
    g_scores = {node: float("inf") for node in graph}
    g_scores[start] = 0
    parents = {}

    while open_set:
        # Get the node with the lowest f_score from the open set
        f_score, current_node = heapq.heappop(open_set)

        if current_node == goal:
            # Reconstruct the path if the goal is reached
            path = []
            while current_node in parents:
                path.insert(0, current_node)
                current_node = parents[current_node]
            path.insert(0, start)
            return path

        closed_set.add(current_node)

        for neighbor in graph[current_node]:
            if neighbor in closed_set:
                continue  # Skip already evaluated nodes

            # Calculate the tentative g_score
            tentative_g_score = (
                g_scores[current_node] + 1
            )  # Assuming all edge weights are 1

            if tentative_g_score < g_scores[neighbor]:
                # This path to the neighbor is better than any previous one
                parents[neighbor] = current_node
                g_scores[neighbor] = tentative_g_score

                # Calculate the heuristic (Euclidean distance)
                h_score = euclidean_distance(neighbor, goal)

                # Calculate the f_score (f = g + h)
                f_score = tentative_g_score + h_score

                heapq.heappush(open_set, (f_score, neighbor))

    # If no path is found
    return None


def euclidean_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
