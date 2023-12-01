"""
TC2008B. Sistemas Multiagentes y Gráficas Computacionales Final Project
Python flask server to interact with Unity. Based on the code provided by Sergio Ruiz.
Collaborators: Octavio Hinojosa, Francisco Martinez Gallardo, Omar Rivera
Date: 2023-11-30
"""
# Import libraries
from flask import Flask, request, jsonify
from model import CityModel
from agent import Car, Traffic_Light, Road
import requests
import json


# Size of the board:
cityModel = None  # City model
currentStep = 0  # Current step of the model

# Create the flask server
app = Flask("Model Server")
url = "http://52.1.3.19:8585/api/attempts"  # Server url for competition


# Initialize the model with the default parameters
@app.route("/init", methods=["GET"])
def initModel():
    global currentStep, cityModel
    if request.method == "GET":
        currentStep = 0  # Reset the current step
        cityModel = CityModel()  # Initialize the model

        return jsonify({"message": "Default parameters recieved, model initiated."})


# Get the agents of the model
@app.route("/getAgents", methods=["GET"])
def getAgents():
    global cityModel  # Get the global city model

    if request.method == "GET":
        agentPositions = [
            {"id": agent.unique_id, "x": x, "y": 0, "z": z}
            for agents, (x, z) in cityModel.grid.coord_iter()
            for agent in agents
            if isinstance(agent, Car)
        ]  # Comprehension list to get the positions of the agents

        # Get the directions of the roads on that position
        for agent in agentPositions:
            try:  # Try to get the direction of the road
                agent["direction"] = cityModel.get_pos_agent(
                    (agent["x"], agent["z"]), Road
                ).direction
            except:  # If there is no road, the car is destroyed
                agent["direction"] = cityModel.get_pos_agent(
                    (agent["x"], agent["z"]), Traffic_Light
                ).direction

        return jsonify(
            {"positions": agentPositions}
        )  # Return the positions of the agents


# Update the model of the model
@app.route("/update", methods=["GET"])
def updateModel():
    global currentStep, cityModel
    if request.method == "GET":
        cityModel.step()

        if currentStep % 100 == 0 and currentStep != 0:
            # sendRequest()  # Send data to the server
            pass

        if currentStep == 1000:
            # Stop the server for competition
            raise KeyboardInterrupt
        currentStep += 1
        return jsonify(
            {
                "message": f"Model updated to step {currentStep}.",
                "currentStep": currentStep,
            }
        )


# Get the traffic lights of the model
@app.route("/getTrafficLights", methods=["GET"])
def getTraffic_Lights():
    global currentStep, cityModel
    if request.method == "GET":
        traffic_light_positions = [
            {
                "id": agent.unique_id,
                "state": 1 if agent.state else 0,
                "direction": agent.direction,
                "x": x,
                "y": 0,
                "z": z,
            }
            for agents, (x, z) in cityModel.grid.coord_iter()
            for agent in agents
            if isinstance(agent, Traffic_Light)
        ]  # Comprehension list to get the positions of the agents, their state and direction (To orient the traffic light on Unity)
        return jsonify({"positions": traffic_light_positions})


def sendRequest():
    cars = cityModel.destroyed
    # Send request to the server for competition
    data = {
        "year": 2023,
        "classroom": 302,
        "name": "Mugiwara no Franks y roroanoa no Omar",
        "num_cars": cars,
    }
    headers = {"Content-type": "application/json"}
    r = requests.post(url, data=json.dumps(data), headers=headers)  # Send the request
    print(r.text, r.status_code)


if __name__ == "__main__":
    app.run(host="localhost", port=8585, debug=True)
