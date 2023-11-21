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

    def countCarAgents(self):
        """Counts the number of car agents in the simulation."""
        count = 0
        for agent in self.schedule.agents:
            if isinstance(agent, Car):
                count += 1
        return count

    def findSpawnPostiion(self):
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

    def step(self):
        """Advance the model by one step."""

        if self.countCarAgents() < self.max_agents:
            spawn = self.findSpawnPostiion()
            if spawn:
                agent = Car(f"c_{self.countCarAgents()}", self)
                self.grid.place_agent(agent, spawn)
                self.schedule.add(agent)

        self.schedule.step()
