from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import *
import json


class CityModel(Model):
    """
    Creates a model based on a city map.

    Args:
        N: Number of agents in the simulation
    """

    def __init__(self, N):
        # Load the map dictionary. The dictionary maps the characters in the map file to the corresponding agent.
        dataDictionary = json.load(open("city_files/mapDictionary.json"))

        self.traffic_lights = []
        self.max_agents = 10
        self.graph = {}
        self.step_count = 0

        # Load the map file. The map file is a text file where each character represents an agent.
        with open("city_files/2022_base.txt") as baseFile:
            lines = baseFile.readlines()
            self.width = len(lines[0]) - 1
            self.height = len(lines)

            self.grid = MultiGrid(self.width, self.height, torus=False)
            self.schedule = RandomActivation(self)

            # Goes through each character in the map file and creates the corresponding agent.
            for r, row in enumerate(lines):
                for c, col in enumerate(row):
                    if col in ["v", "^", ">", "<"]:
                        agent = Road(f"r_{r*self.width+c}", self, dataDictionary[col])
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        edge = self.getFirstConnectedNode(
                            dataDictionary[col], (c, self.height - r - 1)
                        )
                        if edge:
                            self.graph[(c, self.height - r - 1)] = [edge]
                        else:
                            self.graph[(c, self.height - r - 1)] = []

                    elif col in ["S", "s"]:
                        agent = Traffic_Light(
                            f"tl_{r*self.width+c}",
                            self,
                            False if col == "S" else True,
                            int(dataDictionary[col]),
                        )
                        self.grid.place_agent(agent, (c, self.height - r - 1))
                        self.schedule.add(agent)
                        self.traffic_lights.append(agent)

                    elif col == "#":
                        agent = Obstacle(f"ob_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

                    elif col == "D":
                        agent = Destination(f"d_{r*self.width+c}", self)
                        self.grid.place_agent(agent, (c, self.height - r - 1))

        self.num_agents = N
        self.running = True

        # self.fillOtherEdges()

    # Step function. Called every step of the simulation.

    def fillOtherEdges(self):
        """
        This function fills the graph with the other edges from the roads.
        """
        # Iterate through the graph
        for node in self.graph:
            # Iterate through the edges of the node
            if len(self.graph[node]) == 1:
                # If the node has only one edge, then we need to find the other edge
                # Get the direction of the node
                direction = self.getPosAgent(node, Road).direction
                # Append the other edge to the graph
                self.getOtherConnectedNode(direction, node)

    def countCarAgents(self):
        """Counts the number of car agents in the simulation."""
        count = 0
        for agent in self.schedule.agents:
            if isinstance(agent, Car):
                count += 1
        return count

    def findSpawnPostion(self):
        """Finds a spawn location for a car agent."""
        for agent in self.grid.coord_iter():
            if isinstance(agent[0][0], Road):
                direction = agent[0][0].direction
                position = agent[1]
                if self.checkSpawnPosition(position, direction):
                    return position
        return False

    def checkSpawnPosition(self, position, direction):
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
            print("Not valid")
            return False

    def getFirstConnectedNode(self, direction, position):
        """Gets the first connected node to based on direction."""
        edge = None
        if direction == "Right":
            edge = (position[0] + 1, position[1])
        elif direction == "Left":
            edge = (position[0] - 1, position[1])
        elif direction == "Up":
            edge = (position[0], position[1] - 1)
        elif direction == "Down":
            edge = (position[0], position[1] + 1)
        else:
            return False

        if (
            edge[0] >= 0
            and edge[0] < self.width
            and edge[1] >= 0
            and edge[1] < self.height
        ):
            return edge
        else:
            return False

    def getOtherConnectedNode(self, direction, position):
        """Gets the first connected node to based on direction."""
        if direction == "Right" and self.getPosAgent(
            (position[0] + 1, position[0] + 1), Road
        ):
            self.graph[position].append((position[0] + 1, position[1] + 1))
        elif direction == "Right" and self.getPosAgent(
            (position[0] + 1, position[0] - 1), Road
        ):
            self.graph[position].append((position[0] + 1, position[1] - 1))

        elif direction == "Left" and self.getPosAgent(
            (position[0] - 1, position[0] + 1), Road
        ):
            self.graph[position].append((position[0] - 1, position[1] + 1))
        elif direction == "Left" and self.getPosAgent(
            (position[0] - 1, position[0] - 1), Road
        ):
            self.graph[position].append((position[0] - 1, position[1] - 1))
        """
        elif direction == "Up" and self.getPosAgent(
            (position[0] + 1, position[0] + 1), Road
        ):
            self.graph[position].append((position[0] + 1, position[1] + 1))
        elif direction == "Up" and self.getPosAgent(
            (position[0] - 1, position[0] + 1), Road
        ):
            self.graph[position].append((position[0] - 1, position[1] + 1))
        elif direction == "Down" and self.getPosAgent(
            (position[0] + 1, position[0] - 1), Road
        ):
            self.graph[position].append((position[0] + 1, position[1] - 1))
        elif direction == "Down" and self.getPosAgent(
            (position[0] - 1, position[0] - 1), Road
        ):
            self.graph[position].append((position[0] - 1, position[1] - 1))
        """

    def getPosAgent(self, position, object=Road):
        """Gets the road agent on a a position."""

        try:
            for agent in self.grid.get_cell_list_contents([position]):
                if isinstance(agent, object):
                    return agent
        except:
            print(position)
            return False
        return False

    def step(self):
        """Advance the model by one step."""
        if self.step_count % 10 == 0:
            spawn_position = self.findSpawnPostion()
            if spawn_position:
                car = Car(f"c_{self.step_count}", self, (3, 0))
                self.grid.place_agent(car, spawn_position)
                self.schedule.add(car)

        self.step_count += 1
        self.schedule.step()
