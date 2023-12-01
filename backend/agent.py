"""
TC2008B. Sistemas Multiagentes y Gráficas Computacionales Final Project
This file contains the agents used in the model.
Collaborators: Francisco Martinez Gallardo, Omar Rivera,
"""
from mesa import Agent
from a_star import a_star
import random


class Car(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID
        goal: Agent's goal
        time: Time when the agent started moving
        last_move: Last position of the agent
        first_move: Whether this is the first move of the agent
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
        self.time = 0
        self.last_move = None
        self.first_move = True

    def move(self):
        """
        Determines if the agent can move in the direction that was chosen
        """
        path = a_star(
            self.model.graph, self.pos, self.goal
        )  # Find the closest path to the goal.

        # If the path is None, cant get to goal something is wrong.
        if path == None:
            return
        # If the path length is higher than 2, get the next move.
        if len(path) > 2:
            next_move = path[1]
        # Else the agent is in the goal destroy it.
        else:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            self.model.destroyed += 1
            return

        # Check if in the next move there is a car, if so, change the next move.
        next_move = self.check_next_move_is_not_car(next_move)

        # Avoid collision with other cars when changing lanes, when the car is moving diagonally
        # and other car also moved diagonally to your direction.
        next_move = self.avoid_collision(next_move)

        # Check if the next move is a traffic light
        next_move = self.check_traffic_light(next_move)

        # Move the agent to next_move
        self.update_agent(next_move)

    ############################
    ## Movement functions #######
    ############################
    def update_agent(self, next_move):
        """
        This function updates the agent position
        """
        # If its the first move, just place the agent on the grid
        if self.first_move:
            self.first_move = False
        else:
            # Else, move the agent
            if self.pos != next_move:
                self.last_move = self.pos
            self.time = self.model.step_count
            self.model.grid.move_agent(self, next_move)

    def avoid_collision(self, next_move):
        """
        This function checks that the agent do not collide with other cars when changing lanes.
        """
        unchanged_positions = [
            node
            for node in self.model.graph[self.pos]
            if node[0] == self.pos[0] or node[1] == self.pos[1]
        ][
            0
        ]  # Get the unchanged position
        front_agent = self.model.get_pos_agent(
            unchanged_positions, Car
        )  # Check if there is a car in the unchanged position
        if front_agent:
            # Check if the front agent moved diagonally and if it did, do not move to avoid collision
            if front_agent.time == self.model.step_count and (
                front_agent.last_move[0] == next_move[0]
                or front_agent.last_move[1] == next_move[1]
            ):
                return self.pos
        return next_move

    def check_next_move_is_not_car(self, next_move):
        """
        Verifica si el próximo movimiento es hacia una posición ocupada por otro coche.
        Si es así, busca una ruta alternativa o se detiene.
        """
        # Check if the next move is a car
        agent = self.model.get_pos_agent(next_move, Car)
        if agent:
            # Try to move to the other side of the road to avoid collision
            other_moves = self.model.graph[self.pos]
            for move in other_moves:
                if move != next_move and move not in self.model.destinations:
                    # Check again that the next move is not a car
                    agent = self.model.get_pos_agent(move, Car)
                    if not agent:
                        return move
            return self.pos

        return next_move

    def check_sides_for_cars(self):
        """
        This function checks if there are cars in the sides of the car
        """
        # Check that position is on the bounds of the grid

        road = self.model.get_pos_agent(self.pos, Road)
        # Traffic light edge case
        if road is None:
            return False
        try:
            if road.direction == "Up" or road.direction == "Down":
                # Check the right side
                right = (self.pos[0] + 1, self.pos[1])

                agent = self.model.get_pos_agent(right, Car)
                if not agent:
                    self.model.grid.move_agent(agent, self.pos)
                    return True
                # Check the left side
                left = (self.pos[0] - 1, self.pos[1])

                agent = self.model.get_pos_agent(left, Car)
                if not agent:
                    self.model.grid.move_agent(agent, self.pos)
                    return True
            else:
                # Check the up side
                up = (self.pos[0], self.pos[1] + 1)

                agent = self.model.get_pos_agent(up, Car)
                if not agent:
                    self.model.grid.move_agent(agent, self.pos)
                    return True
                # Check the down side
                down = (self.pos[0], self.pos[1] - 1)

                agent = self.model.get_pos_agent(down, Car)
                if not agent:
                    self.model.grid.move_agent(agent, self.pos)
                    return True
        except:
            # Out of bounds position
            return False

    def check_position_on_bounds(self, pos):
        """
        This function checks if the position is on the bounds of the grid
        """
        if (
            pos[0] >= 0
            or pos[0] <= self.model.grid.width - 1
            or pos[1] >= 0
            or pos[1] <= self.model.grid.height - 1
        ):
            return True
        return False

    ############################
    ## Trafic light functions###
    ############################
    def check_traffic_light(self, next_move):
        """
        Checks if the next move is a traffic light
        """
        agent = self.model.get_pos_agent(next_move, Traffic_Light)
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

    def __init__(self, unique_id, model, state=False):
        super().__init__(unique_id, model)
        """
        Creates a new Traffic light.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
            state: Whether the traffic light is green or red
        """
        self.unique_id = unique_id
        self.state = state
        # self.timeToChange = timeToChange
        self.direction = None

        # Get the edge position on edge with direction to the center.

    def step(self):
        """
        Cambia el estado del semáforo en base al tráfico detectado.
        """
        # Find id on self.model.traffic_lights_ids
        time_threshold_for_change = 5  # cambiar las luces cada 5 pasos

        # Change the state of the traffic light
        if self.model.schedule.steps % time_threshold_for_change == 0:
            self.state = not self.state

    # For future implementation add smart traffic lights
    """
    def check_cooldown(self, set_id, other_id):

        Verifica si el semáforo está en cooldown.

        return (
            self.model.traffic_lights_sets[set_id]["cooldown"]
            and self.model.traffic_lights_sets[other_id]["cooldown"]
        )

    def count_amount_of_cars(self, set_id, direction):

        Cuenta la cantidad de coches en la dirección del semáforo.

        # Find the road in the direction of the traffic light
        positions = self.model.traffic_lights_sets[set_id]["traffic_light"]
        car_count = 0

        # Move according to the direction of the traffic light
        positions = self.move_positions(positions, direction)
        while self.check_positions_are_valid(positions):
            positions = self.move_positions(positions, direction)
            car_count += 1
        return car_count

    def move_positions(self, positions, direction):
        if direction == "Up":
            positions = [(pos[0], pos[1] - 1) for pos in positions]
        elif direction == "Down":
            positions = [(pos[0], pos[1] + 1) for pos in positions]
        elif direction == "Left":
            positions = [(pos[0] + 1, pos[1]) for pos in positions]
        elif direction == "Right":
            positions = [(pos[0] - 1, pos[1]) for pos in positions]
        return positions

    def check_positions_are_valid(self, positions):

        This function checks if the positions are valid

        for pos in positions:
            if not self.check_position_on_bounds(pos):
                return False
            if not self.check_if_car_in_position(pos):
                return False
        return True

    def check_position_on_bounds(self, pos):

        This function checks if the position is on the bounds of the grid

        if (
            pos[0] >= 0
            or pos[0] <= self.model.grid.width - 1
            or pos[1] >= 0
            or pos[1] <= self.model.grid.height - 1
        ):
            return True
        return False

    def check_if_car_in_position(self, pos):

        This function checks if there is a car in the position

        agent = self.model.get_pos_agent(pos, Car)
        if agent:
            return True
        return False
    """


#####################################
## Other not intelligent agents #####
#####################################


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
