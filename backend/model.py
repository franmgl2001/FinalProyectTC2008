"""
TC2008B. Sistemas Multiagentes y Gráficas Computacionales Final Project
Python model declaration script.
Collaborators:Francisco Martinez Gallardo, Omar Rivera
Date: 2023-11-30
"""
from mesa import Model
from mesa.time import RandomActivation, BaseScheduler
from mesa.space import MultiGrid
from agent import *
import json
import random


class CityModel(Model):
    """
    Creates a model based on a city map.
    """

    def __init__(self):
        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
        data_dictionary = json.load(open("city_files/mapDictionary.json"))

        self.traffic_lights = []  # List of traffic lights
        self.graph = {}  # Graph of the city
        self.step_count = 0  # Step count
        self.agent_count = 0  # Agent count
        self.destinations = []  # List of destinations
        self.destroyed = 0  # Number of destroyed cars

        # For future implementation to make the traffic light intelligent
        # self.traffic_lights_sets = {}
        # self.traffic_lights_ids = {}

        # Load the map file. The map file is a text file where each character represents an agent.
        with open("city_files/2023_base.txt") as base_file:
            lines = base_file.readlines()
            self.width = len(lines[0]) - 1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus=False)
            self.schedule = BaseScheduler(self)

            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    # Add the Road agent to the grid and the schedule
                    if col in ["v", "^", ">", "<"]:
                        agent = Road(f"r_{r*self.width+c}", self, data_dictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        edge = self.get_first_connected_node(
                            data_dictionary[col], (c, self.height - r - 1)
                        )
                        if edge:
                            self.graph[(c, self.height - r - 1)] = [edge]
                        else:
                            self.graph[(c, self.height - r - 1)] = []
                    # Add the Traffic Light agent to the grid and the schedule
                    elif col in ["S", "s"]:
                        agent = Traffic_Light(
                            f"S_{r*self.width+c}", self, False if col == "S" else True
                        )
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)

                    # Add the Obstacle agent to the grid and the schedule
                    elif col == "#":
                        agent = Obstacle(f"ob_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    # Add the Destination agent to the grid and the schedule
                    elif col == "D":
                        agent = Destination(f"d_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.destinations.append(agent.pos)

        self.running = True

        # Add the traffic light grid as edges to the graph
        self.fill_traffic_lights_edges()
        # Add the other edges to the graph
        self.fill_other_edges()
        # Add all destiniy nodes and edges to the graph
        self.add_all_destinies_to_graph()

        # For future implementation to make the traffic light intelligent
        # self.()

    # Step function. Called every step of the simulation.

    ############################
    #### Graph functions #######
    ############################

    def get_first_connected_node(self, direction, position):
        """Gets the first connected node to based on direction."""
        # Get the edge based on the direction
        edge = None
        if direction == "Right":
            edge = (position[0] + 1, position[1])
        elif direction == "Left":
            edge = (position[0] - 1, position[1])
        elif direction == "Up":
            edge = (position[0], position[1] + 1)
        elif direction == "Down":
            edge = (position[0], position[1] - 1)
        else:
            return False
        # Check if the edge is in the grid
        if (
            edge[0] >= 0
            and edge[0] < self.width
            and edge[1] >= 0
            and edge[1] < self.height
        ):
            return edge
        else:
            return False

    # Traffic lights edges
    def fill_traffic_lights_edges(self):
        """
        This function fills the graph with the edges from the traffic lights.
        """
        # Iterate through the traffic lights
        for traffic_light in self.traffic_lights:
            # Get traffic light neighborhood and detect the road agents
            neighborhood = self.grid.get_neighborhood(
                traffic_light.pos, moore=False, include_center=False
            )
            for neighbor in neighborhood:
                if self.get_pos_agent(neighbor, Road):
                    # Get the direction of the road
                    agent = self.get_pos_agent(neighbor, Road)
                    direction = agent.direction
                    # Check if the traffic light is in the right position
                    if self.graph[agent.pos][0] == traffic_light.pos:
                        traffic_light_agent = self.get_pos_agent(
                            traffic_light.pos, Traffic_Light
                        )
                        traffic_light_agent.direction = direction
                        self.graph[traffic_light.pos] = [
                            self.generate_light_edge(traffic_light.pos, direction)
                        ]

    def generate_light_edge(self, traffic_light_pos, direction):
        """
        This function generates the edge of a traffic light.
        """
        # Get the edge based on the direction
        if direction == "Right":
            return (traffic_light_pos[0] + 1, traffic_light_pos[1])
        elif direction == "Left":
            return (traffic_light_pos[0] - 1, traffic_light_pos[1])
        elif direction == "Up":
            return (traffic_light_pos[0], traffic_light_pos[1] + 1)
        elif direction == "Down":
            return (traffic_light_pos[0], traffic_light_pos[1] - 1)
        else:
            return False
        # Get traffic light neighborhood and detect the road agents

    # Extra edges
    def fill_other_edges(self):
        """
        This function fills the graph with the other edges from the roads.
        """
        # Iterate through the graph
        for node in self.graph:
            # Iterate through the edges of the node
            if len(self.graph[node]) == 1:
                # If the node has only one edge, then we need to find the other edges
                if self.get_pos_agent(node, Road):
                    direction = self.get_pos_agent(node, Road).direction
                    self.get_other_connected_node(direction, node)
                # If the node has only one edge, then we need to find the other edges
                elif self.get_pos_agent(node, Traffic_Light):
                    direction = self.get_pos_agent(node, Traffic_Light).direction
                    self.get_other_connected_node(direction, node)

    def check_that_edge_do_not_collide(self, node, interest_node):
        """
        This function checks that the edge do not collide with another edge.
        """
        # Iterate through the edges of the node
        for n in self.graph[node]:
            for i in self.graph[interest_node]:
                if n == i:
                    return False
        return True

    def get_other_connected_node(self, direction, position):
        """Gets the first connected node to based on direction."""

        if position[1] != self.height - 1:
            # Check if the node is not in the top of the grid on other front directions
            # In all the cases, add all possible directions
            if (
                direction == "Right"
                and self.get_pos_agent((position[0] + 1, position[1] + 1), Road)
                and self.check_that_edge_do_not_collide(
                    position, (position[0] + 1, position[1] + 1)
                )
            ):
                self.graph[position].append((position[0] + 1, position[1] + 1))

            if (
                direction == "Left"
                and self.get_pos_agent((position[0] - 1, position[1] + 1), Road)
                and self.check_that_edge_do_not_collide(
                    position, (position[0] - 1, position[1] + 1)
                )
            ):
                self.graph[position].append((position[0] - 1, position[1] + 1))

        if position[1] != 0:
            if (
                direction == "Right"
                and self.get_pos_agent((position[0] + 1, position[1] - 1), Road)
                and self.check_that_edge_do_not_collide(
                    position, (position[0] + 1, position[1] - 1)
                )
            ):
                self.graph[position].append((position[0] + 1, position[1] - 1))

            if (
                direction == "Left"
                and self.get_pos_agent((position[0] - 1, position[1] - 1), Road)
                and self.check_that_edge_do_not_collide(
                    position, (position[0] - 1, position[1] - 1)
                )
            ):
                self.graph[position].append((position[0] - 1, position[1] - 1))

        if position[0] != self.width - 1:
            if (
                direction == "Up"
                and self.get_pos_agent((position[0] + 1, position[1] + 1), Road)
                and self.check_that_edge_do_not_collide(
                    position, (position[0] + 1, position[1] + 1)
                )
            ):
                self.graph[position].append((position[0] + 1, position[1] + 1))

            if (
                direction == "Down"
                and self.get_pos_agent((position[0] + 1, position[1] - 1), Road)
                and self.check_that_edge_do_not_collide(
                    position, (position[0] + 1, position[1] - 1)
                )
            ):
                self.graph[position].append((position[0] + 1, position[1] - 1))

        if position[0] != 0:
            if (
                direction == "Up"
                and self.get_pos_agent((position[0] - 1, position[1] + 1), Road)
                and self.check_that_edge_do_not_collide(
                    position, (position[0] - 1, position[1] + 1)
                )
            ):
                self.graph[position].append((position[0] - 1, position[1] + 1))

            if (
                direction == "Down"
                and self.get_pos_agent((position[0] - 1, position[1] - 1), Road)
                and self.check_that_edge_do_not_collide(
                    position, (position[0] - 1, position[1] - 1)
                )
            ):
                self.graph[position].append((position[0] - 1, position[1] - 1))

    def get_pos_agent(self, position, object=Road):
        """Gets the road agent on a a position."""
        for agent in self.grid.get_cell_list_contents([position]):
            # Check if the agent is the given object
            if isinstance(agent, object):
                return agent

        return False

    def count_car_agents(self):
        """Counts the number of car agents in the simulation."""
        count = 0
        for agent in self.schedule.agents:
            # Count the number of car agents
            if isinstance(agent, Car):
                count += 1
        return count

    ############################
    #### Spawn functions #######
    ############################

    def find_spawn_postions(self):
        """Finds a spawn location for a car agent."""
        possibleSpawnLocations = []
        for agent in self.grid.coord_iter():
            if isinstance(agent[0][0], Road):
                direction = agent[0][0].direction
                position = agent[1]
                if self.check_spawn_position(position, direction):
                    possibleSpawnLocations.append(position)

        # Return 4 unique random spawn locations
        for spawn in possibleSpawnLocations:
            # Check if car is already in the spawn location
            if self.get_pos_agent(spawn, Car):
                possibleSpawnLocations.remove(spawn)

        return possibleSpawnLocations

    def check_spawn_position(self, position, direction):
        """Checks if a spawn position is valid."""
        if position[0] == 0 and direction == "Right":
            return True
        elif position[0] == self.width - 1 and direction == "Left":
            return True
        elif position[1] == 0 and direction == "Up":
            return True
        elif position[1] == self.width - 1 and direction == "Down":
            return True
        else:
            return False

    def spawn_agents(self):
        """Spawns car agents."""
        spawn_positions = self.find_spawn_postions()
        # From the possible spawn locations, choose 4 random spawn locations
        for spawn in spawn_positions:
            # Choose a random destiny
            destiny = random.choice(self.destinations)
            # Create the car agent
            car = Car(self.agent_count, self, destiny)
            self.agent_count += 1
            # Add the car agent to the grid and the schedule
            self.grid.place_agent(car, spawn)
            self.schedule.add(car)

    ############################
    #### Destiny functions #####
    ############################

    def add_all_destinies_to_graph(self):
        """Adds all destinies to the graph."""
        for destiny in self.destinations:
            self.add_destiny_to_graph(destiny)

    def add_destiny_to_graph(self, destiny):
        """Adds a destiny to the graph."""
        # Make destiny reachable from veritical and horzontal road neighbors
        neighborhood = self.grid.get_neighborhood(
            destiny, moore=False, include_center=False
        )
        for neighbor in neighborhood:
            # Check that neighbor is a road
            if self.get_pos_agent(neighbor, Road):
                # Check that the road is horizontal or vertical to the destiny
                if (
                    neighbor[0] == destiny[0]
                    or neighbor[1] == destiny[1]
                    and neighbor != destiny
                ):
                    self.graph[neighbor].append(destiny)
                    self.graph[destiny] = []

    ########################################################
    #### Intellignet traffic light future implementation ###
    ########################################################

    """
    def set_traffic_lights_sets(self):
         #Sets the traffic lights sets.

        cont = 0
        done = []
        for traffic_light in self.traffic_lights:
            # Get traffic light neighborhood and get the
            neighborhood = self.grid.get_neighborhood(
                traffic_light.pos, moore=False, include_center=False
            )
            for neighbor in neighborhood:
                if self.get_pos_agent(neighbor, Traffic_Light) and neighbor not in done:
                    self.traffic_lights_sets[cont] = {
                        "traffic_light": [
                            traffic_light.pos,
                            neighbor,
                        ],
                        "invocation": 0,
                        "cooldown": False,
                        "toGreen": False,
                    }
                    self.traffic_lights_ids[traffic_light.pos] = cont
                    self.traffic_lights_ids[neighbor] = cont

                    done.append(neighbor)
                    done.append(traffic_light.pos)
                    cont += 1

        self.addTrafficLightsNeighborSets()

    # Add traffc lights neighbor sets
    def addTrafficLightsNeighborSets(self):
        #Adds the traffic lights neighbor sets
        for key1, value1 in self.traffic_lights_sets.items():
            for key2, value2 in self.traffic_lights_sets.items():
                if key1 != key2:
                    # Check if any of the traffic lights in value1 are neighbors of those in value2
                    for coord1 in value1["traffic_light"]:
                        for coord2 in value2["traffic_light"]:
                            if self.coordinate_difference_chec(coord1, coord2):
                                self.traffic_lights_sets[key1]["neighbors"] = key2

    def coordinate_difference_chec(self, coord1, coord2):
        #Checks if the difference between two coordinates is 1.
        if abs(coord1[0] - coord2[0]) == 1 and abs(coord1[1] - coord2[1]) == 1:
            return True
        else:
            return False
    """

    def step(self):
        """Advance the model by one step."""
        if self.step_count % 3 == 0:
            self.spawn_agents()
        if len(self.find_spawn_postions()) == 0:
            self.running = False

        self.step_count += 1
        self.schedule.step()
