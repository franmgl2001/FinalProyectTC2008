from mesa import Agent
from aStar import aStar


class Car(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID
        direction: Randomly chosen direction chosen from one of eight directions
    """

    def __init__(self, unique_id, model, goal):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        self.goal = goal

    def move(self):
        """
        Determines if the agent can move in the direction that was chosen
        """
        # Check that the agent in possible_steps are rooads and get the direction of the road

        path = aStar(self.model.graph, self.pos, self.goal)
        if len(path) > 1:
            next_move = path[1]
        else:
            return

        next_move = self.checkTrafficLight(next_move)

        # Move the agent to next_move
        self.model.grid.move_agent(self, next_move)

    ############################
    ## Trafic light functions###
    ############################
    def checkTrafficLight(self, next_move):
        """
        Checks if the next move is a traffic light
        """
        agent = self.model.getPosAgent(next_move, Traffic_Light)
        if agent:
            if agent.state:
                # If it is green, move
                self.model.grid.move_agent(self, next_move)
                return next_move
            else:
                return self.pos
        return next_move

    def step(self):
        """
        Determines the new direction it will take, and then moves

        """
        self.move()


class Traffic_Light(Agent):
    """
    Traffic light. Where the traffic lights are in the grid.
    """

    def __init__(self, unique_id, model, state=False, timeToChange=10):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green or red
            timeToChange: After how many step should the traffic light change color 
        """
        self.state = state
        self.timeToChange = timeToChange

        # Get the edge position on edge with direction to the center.

    def step(self):
        """
        To change the state (green or red) of the traffic light in case you consider the time to change of each traffic light.
        """
        if self.model.schedule.steps % self.timeToChange == 0:
            self.state = not self.state


class Destination(Agent):
    """
    Destination agent. Where each car should go.
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass


class Obstacle(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass


class Road(Agent):
    """
    Road agent. Determines where the cars can move, and in which direction.
    """

    def __init__(self, unique_id, model, direction="Left"):
        """
        Creates a new road.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            direction: Direction where the cars can move
        """
        super().__init__(unique_id, model)
        self.direction = direction

    def step(self):
        pass
