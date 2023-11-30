from mesa import Agent
from aStar import aStar
import random


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
        self.time = 0
        self.last_move = None
        self.first_move = True

    def move(self):
        """
        Determines if the agent can move in the direction that was chosen
        """
        # Check that the agent in possible_steps are rooads and get the direction of the road
        path = aStar(self.model.graph, self.pos, self.goal)

        if path == None:
            return
        if len(path) > 2:
            next_move = path[1]
        else:
            self.model.grid.remove_agent(self)
            self.model.schedule.remove(self)
            self.model.destroyed += 1
            return

        # Check if the next move is a car
        next_move = self.checkNextMoveIsNotCar(next_move)

        # Check if the next move is a traffic light
        next_move = self.avoid_collision(next_move)

        # Check if the next move is a traffic light
        next_move = self.checkTrafficLight(next_move)

        # Move the agent to next_move
        if self.first_move:
            self.first_move = False
        else:
            if self.pos != next_move:
                self.last_move = self.pos
            self.time = self.model.step_count

            self.model.grid.move_agent(self, next_move)

    def avoid_collision(self, next_move):
        unchanged_positions = [
            node
            for node in self.model.graph[self.pos]
            if node[0] == self.pos[0] or node[1] == self.pos[1]
        ][0]
        # Find agent in the unchanged positions
        front_agent = self.model.getPosAgent(unchanged_positions, Car)
        if front_agent:
            if front_agent.time == self.model.step_count and (
                front_agent.last_move[0] == next_move[0]
                or front_agent.last_move[1] == next_move[1]
            ):
                return self.pos
        return next_move

    def checkNextMoveIsNotCar(self, next_move):
        """
        Verifica si el próximo movimiento es hacia una posición ocupada por otro coche.
        Si es así, busca una ruta alternativa o se detiene.
        """
        # Check if the next move is a car
        agent = self.model.getPosAgent(next_move, Car)
        if agent:
            # Try to move to the other side of the road to avoid collision
            other_moves = self.model.graph[self.pos]
            for move in other_moves:
                if move != next_move and move not in self.model.destinations:
                    # Check again that the next move is not a car
                    agent = self.model.getPosAgent(move, Car)
                    if not agent:
                        return move
            return self.pos

        return next_move

    def check_sides_for_cars(self):
        """
        This function checks if there are cars in the sides of the car
        """
        # Check that position is on the bounds of the grid

        road = self.model.getPosAgent(self.pos, Road)
        # Traffic light edge case
        if road is None:
            return False
        try:
            if road.direction == "Up" or road.direction == "Down":
                # Check the right side
                right = (self.pos[0] + 1, self.pos[1])

                agent = self.model.getPosAgent(right, Car)
                if not agent:
                    self.model.grid.move_agent(agent, self.pos)
                    return True
                # Check the left side
                left = (self.pos[0] - 1, self.pos[1])

                agent = self.model.getPosAgent(left, Car)
                if not agent:
                    self.model.grid.move_agent(agent, self.pos)
                    return True
            else:
                # Check the up side
                up = (self.pos[0], self.pos[1] + 1)

                agent = self.model.getPosAgent(up, Car)
                if not agent:
                    self.model.grid.move_agent(agent, self.pos)
                    return True
                # Check the down side
                down = (self.pos[0], self.pos[1] - 1)

                agent = self.model.getPosAgent(down, Car)
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
        self.unique_id = unique_id
        self.state = state
        self.timeToChange = timeToChange
        self.direction = None

        # Get the edge position on edge with direction to the center.

    def step(self):
        """
        Cambia el estado del semáforo en base al tráfico detectado.
        """
        # Find id on self.model.traffic_lights_ids

        # Puedes ajustar estos valores según necesites
        time_threshold_for_change = 5  # cambiar cada 10 pasos

        if self.model.schedule.steps % time_threshold_for_change == 0:
            self.state = not self.state

    def check_cooldown(self, set_id, other_id):
        """
        Verifica si el semáforo está en cooldown.
        """
        return (
            self.model.traffic_lights_sets[set_id]["cooldown"]
            and self.model.traffic_lights_sets[other_id]["cooldown"]
        )

    def count_amount_of_cars(self, set_id, direction):
        """
        Cuenta la cantidad de coches en la dirección del semáforo.
        """
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
        """
        This function checks if the positions are valid
        """
        for pos in positions:
            if not self.check_position_on_bounds(pos):
                return False
            if not self.check_if_car_in_position(pos):
                return False
        return True

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

    def check_if_car_in_position(self, pos):
        """
        This function checks if there is a car in the position
        """
        agent = self.model.getPosAgent(pos, Car)
        if agent:
            return True
        return False


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
