﻿// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// C# client to interact with Python. Based on the code provided by Sergio Ruiz.
// Octavio Navarro. October 2023

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class AgentData
{
    /*
    The AgentData class is used to store the data of each agent.
    
    Attributes:
        id (string): The id of the agent.
        x (float): The x coordinate of the agent.
        y (float): The y coordinate of the agent.
        z (float): The z coordinate of the agent.
    */
    public string id;
    public float x, y, z;
    public int state;
    
    public AgentData(string id, int state, float x, float y, float z)
    {
        this.id = id;
        this.state = state;
        this.x = x;
        this.y = y;
        this.z = z;
    }
}

[Serializable]

public class AgentsData
{
    /*
    The AgentsData class is used to store the data of all the agents.

    Attributes:
        positions (list): A list of AgentData objects.
    */
    public List<AgentData> positions;

    public AgentsData() => this.positions = new List<AgentData>();
}

public class AgentController : MonoBehaviour
{
    /*
    The AgentController class is used to control the agents in the simulation.

    Attributes:
        serverUrl (string): The url of the server.
        getAgentsEndpoint (string): The endpoint to get the agents data.
        sendConfigEndpoint (string): The endpoint to send the configuration.
        updateEndpoint (string): The endpoint to update the simulation.
        agentsData (AgentsData): The data of the agents.
        obstacleData (AgentsData): The data of the obstacles.
        agents (Dictionary<string, GameObject>): A dictionary of the agents.
        prevPositions (Dictionary<string, Vector3>): A dictionary of the previous positions of the agents.
        currPositions (Dictionary<string, Vector3>): A dictionary of the current positions of the agents.
        updated (bool): A boolean to know if the simulation has been updated.
        started (bool): A boolean to know if the simulation has started.
        agentPrefab (GameObject): The prefab of the agents.
        obstaclePrefab (GameObject): The prefab of the obstacles.
        floor (GameObject): The floor of the simulation.
        NAgents (int): The number of agents.
        width (int): The width of the simulation.
        height (int): The height of the simulation.
        timeToUpdate (float): The time to update the simulation.
        timer (float): The timer to update the simulation.
        dt (float): The delta time.
    */
    string serverUrl = "http://localhost:8585";
    string getAgentsEndpoint = "/getAgents";
    string getTrafficLightsEndpoint = "/getTrafficLights";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    AgentsData agentsData, obstacleData, trafficLightsData;
    Dictionary<string, GameObject> agents;
    Dictionary<string, GameObject> trafficLightsAgents;
    Dictionary<string, Vector3> prevPositions, currPositions;

    bool updated = false, started = false;

    public GameObject agentPrefab, TrafficLightPrefab;
    public int NAgents, width, height;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    void Start()
    {
        agentsData = new AgentsData();
        obstacleData = new AgentsData();

        prevPositions = new Dictionary<string, Vector3>();
        currPositions = new Dictionary<string, Vector3>();

        agents = new Dictionary<string, GameObject>();
        trafficLightsAgents = new Dictionary<string, GameObject>();
        
        timer = timeToUpdate;

        // Launches a couroutine to send the configuration to the server.
        StartCoroutine(SendConfiguration());
        StartCoroutine(GetTrafficData());
    }

    private void Update() 
    {
        if(timer < 0)
        {
            timer = timeToUpdate;
            updated = false;
            StartCoroutine(UpdateSimulation());
        }

        if (updated)
        {
            timer -= Time.deltaTime;
            dt = 1.0f - (timer / timeToUpdate);

            // Iterates over the agents to update their positions.
            // The positions are interpolated between the previous and current positions.
            foreach(var agent in currPositions)
            {
                Vector3 currentPosition = agent.Value;
                // Check 
                Vector3 previousPosition = prevPositions[agent.Key];
                /*
                Debug.Log(agent.Key);
                Vector3 currentPosition = agent.Value;
                // Check 
                Vector3 previousPosition = prevPositions[agent.Key];

                Vector3 interpolated = Vector3.Lerp(previousPosition, currentPosition, dt);
                Vector3 direction = currentPosition - interpolated;

                agents[agent.Key].transform.localPosition = interpolated;
                if(direction != Vector3.zero) agents[agent.Key].transform.rotation = Quaternion.LookRotation(direction);
            }
            */
            }
            // float t = (timer / timeToUpdate);
            // dt = t * t * ( 3f - 2f*t);
            
        }
    }
 
    IEnumerator UpdateSimulation()
    {
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetTrafficData());
        }
    }

    IEnumerator SendConfiguration()
    {
        /*
        The SendConfiguration method is used to send the configuration to the server.

        It uses a WWWForm to send the data to the server, and then it uses a UnityWebRequest to send the form.
        */

        UnityWebRequest www = UnityWebRequest.Get(serverUrl + sendConfigEndpoint);
        www.SetRequestHeader("Content-Type", "application/x-www-form-urlencoded");

        yield return www.SendWebRequest();

        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log("Configuration upload complete!");
            Debug.Log("Getting Agents positions");

            // Once the configuration has been sent, it launches a coroutine to get the agents data.
            StartCoroutine(GetAgentsData());
            StartCoroutine(GetTrafficData());
        }
    }

    IEnumerator GetAgentsData() 
    {
        // The GetAgentsData method is used to get the agents data from the server.
        
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getAgentsEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            // Once the data has been received, it is stored in the agentsData variable.
            // Then, it iterates over the agentsData.positions list to update the agents positions.
            agentsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);

            foreach(AgentData agent in agentsData.positions)
            {
 
                    
                    Vector3 newAgentPosition = new Vector3(agent.x, agent.y, agent.z);
                    Debug.Log("newAgentPosition: " + newAgentPosition);
                        // Check that agent id exists in agents dictionary

                        if(!agents.ContainsKey(agent.id))
                        {
                            prevPositions[agent.id] = newAgentPosition;
                            agents[agent.id] = Instantiate(agentPrefab, Vector3.zero, Quaternion.identity);
                            ApplyTransforms applyTransforms = agents[agent.id].GetComponent<ApplyTransforms>();
                            applyTransforms.getPosition(newAgentPosition, true);
                            //applyTransforms.endPosition = newAgentPosition;
                        }
                        else
                        {
                            ApplyTransforms applyTransforms = agents[agent.id].GetComponent<ApplyTransforms>();  
                            applyTransforms.getPosition(newAgentPosition, false);
                            
                            //applyTransforms.endPosition = newAgentPosition;                   


                        }
            }

            updated = true;
            if(!started) started = true;
        }
    }

    IEnumerator GetTrafficData() 
{
        UnityWebRequest www = UnityWebRequest.Get(serverUrl + getTrafficLightsEndpoint);
        yield return www.SendWebRequest();
        
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            // Once the data has been received, it is stored in the agentsData variable.
            // Then, it iterates over the agentsData.positions list to update the agents positions.
            trafficLightsData = JsonUtility.FromJson<AgentsData>(www.downloadHandler.text);
        }
         foreach(AgentData agent in  trafficLightsData.positions)
            {
                Vector3 newAgentPosition = new Vector3(agent.x, agent.y, agent.z);
                // Check if the agent exists in the trafficLightsAgents dictionary
                if (!trafficLightsAgents.ContainsKey(agent.id))
                {
                    trafficLightsAgents[agent.id] = Instantiate(TrafficLightPrefab, newAgentPosition, Quaternion.identity);
                    trafficLightsAgents[agent.id].GetComponent<LightsColor>().state = agent.state;
                }
                else
                {
                    trafficLightsAgents[agent.id].GetComponent<LightsColor>().state = agent.state;
                }
                    

                
            }

}


}



