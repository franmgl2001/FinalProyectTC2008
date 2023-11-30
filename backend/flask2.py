# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# Python flask server to interact with Unity. Based on the code provided by Sergio Ruiz.
# Octavio Navarro. October 2023git

from flask import Flask, request, jsonify
from model import CityModel
from agent import Car, Traffic_Light
import requests
import json


# Size of the board:
number_agents = 10
cityModel = None
currentStep = 0

app = Flask("Traffic example")
url = "http://52.1.3.19:8585/api/validate_attempt"


@app.route("/init", methods=["GET", "POST"])
def initModel():
    global currentStep, cityModel
    if request.method == "GET":
        currentStep = 0
        cityModel = CityModel()

        return jsonify({"message": "Default parameters recieved, model initiated."})


@app.route("/getAgents", methods=["GET"])
def getAgents():
    global cityModel

    if request.method == "GET":
        agentPositions = [
            {"id": agent.unique_id, "x": x, "y": 0, "z": z}
            for agents, (x, z) in cityModel.grid.coord_iter()
            for agent in agents
            if isinstance(agent, Car)
        ]

        return jsonify({"positions": agentPositions})


@app.route("/update", methods=["GET"])
def updateModel():
    global currentStep, cityModel
    if request.method == "GET":
        cityModel.step()
        currentStep += 1
        sendRequest()

        return jsonify(
            {
                "message": f"Model updated to step {currentStep}.",
                "currentStep": currentStep,
            }
        )


@app.route("/getTrafficLights", methods=["GET"])
def getTraffic_Lights():
    global currentStep, cityModel
    if request.method == "GET":
        traffic_light_positions = [
            {
                "id": agent.unique_id,
                "state": 1 if agent.state else 0,
                "x": x,
                "y": 0,
                "z": z,
            }
            for agents, (x, z) in cityModel.grid.coord_iter()
            for agent in agents
            if isinstance(agent, Traffic_Light)
        ]
        return jsonify({"positions": traffic_light_positions})


def sendRequest():
    cars = len(
        [
            {"id": agent.unique_id, "x": x, "y": 0, "z": z}
            for agents, (x, z) in cityModel.grid.coord_iter()
            for agent in agents
            if isinstance(agent, Car)
        ]
    )
    # Send data to the server
    data = {"year": 2023, "classroom": 302, "name": "Equipo7", "num_cars": cars}
    headers = {"Content-type": "application/json"}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print(r.status_code)


if __name__ == "__main__":
    app.run(host="localhost", port=8585, debug=True)
