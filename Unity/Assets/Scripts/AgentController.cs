// TC2008B. Sistemas Multiagentes y Gráficas Computacionales
// C# client to interact with Python. Based on the code provided by Sergio Ruiz.
// Octavio Navarro, Francisco Martinez Gallardo, Omar Rivera

using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
// Define the AgentData class to store the data of each agent.
public class AgentData
{
    public string id;
    public float x, y, z;
    public int state; // State used on the traffic lights
    public string direction;// Direction used on the traffic lights
    
    // Constructor of the AgentData class.
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
        getTrafficLightsEndpoint (string): The endpoint to get the traffic lights data.
        sendConfigEndpoint (string): The endpoint to send the configuration to the server.
        updateEndpoint (string): The endpoint to update the simulation.
        agentsData (AgentsData): The data of the agents.
        agents (Dictionary<string, GameObject>): A dictionary of the agents.
        trafficLightsAgents (Dictionary<string, GameObject>): A dictionary of the traffic lights.
        agentPrefab (GameObject): The prefab of the agents.
        trafficLightPrefab (GameObject): The prefab of the traffic lights.
        timeToUpdate (float): The time to update the simulation.
        timer (float): The timer to update the simulation.
        dt (float): The delta time.
    */
    string serverUrl = "http://localhost:8585";
    string getAgentsEndpoint = "/getAgents";
    string getTrafficLightsEndpoint = "/getTrafficLights";
    string sendConfigEndpoint = "/init";
    string updateEndpoint = "/update";
    AgentsData agentsData, trafficLightsData;
    Dictionary<string, GameObject> agents;
    Dictionary<string, GameObject> trafficLightsAgents;
    List<string> keysToRemove = new List<string>();
    bool updated = false, started = false;
    public GameObject agentPrefab, TrafficLightPrefab;
    public float timeToUpdate = 5.0f;
    private float timer, dt;

    void Start()
    {
        // Initialize the agentsData and agents variables.
        agentsData = new AgentsData();
        agents = new Dictionary<string, GameObject>();
        trafficLightsAgents = new Dictionary<string, GameObject>();
        
        timer = timeToUpdate;

        // Launches a couroutine to send the configuration to the server.
        StartCoroutine(SendConfiguration()); // Start the simulation
        StartCoroutine(getTrafficLightData()); // Get the traffic lights data and create the traffic lights
    }

    private void Update() 
    {
        // Update the simulation every timeToUpdate seconds.
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
            
        }
    }
 
    IEnumerator UpdateSimulation()
    {
        /*
        The UpdateSimulation method is used to update the simulation.

        It uses a UnityWebRequest to send a GET request to the server.
        */

        UnityWebRequest www = UnityWebRequest.Get(serverUrl + updateEndpoint);
        yield return www.SendWebRequest();
 
        if (www.result != UnityWebRequest.Result.Success)
            Debug.Log(www.error);
        else 
        {
            //Once the simulation has been updated, start a coroutine to get the agents data and traffic data for it to move.
            StartCoroutine(GetAgentsData());
            StartCoroutine(getTrafficLightData());
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
            StartCoroutine(getTrafficLightData());
        }
    }

    IEnumerator GetAgentsData() 
    {
        /*
        The GetAgentsData method is used to get the agents data from the server.

        It uses a UnityWebRequest to send a GET request to the server.
        */
        
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
                    
                        // Check that agent id exists in agents dictionary
                        if(!agents.ContainsKey(agent.id))
                        {
                            // Instantiate the agent prefab and add it to the agents dictionary
                            agents[agent.id] = Instantiate(agentPrefab, Vector3.zero, Quaternion.identity);
                            // Get the ApplyTransforms component of the agent and set the position
                            ApplyTransforms applyTransforms = agents[agent.id].GetComponent<ApplyTransforms>();
                            // Send the new position to the ApplyTransforms component for it to move
                            applyTransforms.movePosition(newAgentPosition, true, agent.direction);
                        }
                        else
                        {
                            // Get the ApplyTransforms component of the agent and set the position
                            ApplyTransforms applyTransforms = agents[agent.id].GetComponent<ApplyTransforms>();  
                            // Send the new position to the ApplyTransforms component for it to move
                            applyTransforms.movePosition(newAgentPosition, false, agent.direction);                 
                        }
                    
            }

            removeAgent();

            // Find agents that are not in the agentsData.positions list and destroy them.

            updated = true;
            if(!started) started = true;
        }

        void removeAgent()
        {
            /*
            The removeAgent method is used to remove the agents that are not in the agentsData.positions list.
            */
            // Find agents that are not in the agentsData.positions list and destroy them.
            foreach (string key in agents.Keys)
            {
                // If the agent is not in the agentsData.positions list, destroy it.
                if (!agentsData.positions.Exists(agent => agent.id == key))
                {
                    // Destroy the agent
                    Debug.Log("Destroying agent: " + key);
                    ApplyTransforms applyTransforms = agents[key].GetComponent<ApplyTransforms>();  
                    applyTransforms.removeWheels();
                    Destroy(agents[key]);
                    keysToRemove.Add(key);

                }
            }
            // Remove the agents from the agents dictionary.
            foreach (string key in keysToRemove)
            {
                agents.Remove(key);
            }
        }
    }

    IEnumerator getTrafficLightData() 
{
        /*
        The getTrafficLightData method is used to get the agents data from the server.
        */
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
                // Get the position of the agent
                Vector3 newAgentPosition = new Vector3(agent.x, agent.y, agent.z);

                
                int angle = getTrafficLightAngle(agent.direction);
                // Check if the agent exists in the trafficLightsAgents dictionary
                if (!trafficLightsAgents.ContainsKey(agent.id))
                {
                    // Instantiate the agent prefab and add it to the trafficLightsAgents dictionary
                    trafficLightsAgents[agent.id] = Instantiate(TrafficLightPrefab, newAgentPosition,  Quaternion.Euler(0, angle, 0));
                    // Get the ApplyTransforms component of the agent and set the light color
                    trafficLightsAgents[agent.id].GetComponent<LightsColor>().state = agent.state;
                }
                else
                {
                    // Get the ApplyTransforms component of the agent and set the light color
                    trafficLightsAgents[agent.id].GetComponent<LightsColor>().state = agent.state;
                }
                    

                
            }

    int getTrafficLightAngle(string direction)
    {
        /*
        The getTrafficLightAngle method is used to get the angle of the traffic light.
        */
        switch (direction)
        {
            case "Left":
                return 0;
            case "Right":   
                return 180;
            case "Up":
                return 270;
            case "Down":
                return 90;
            default:
                return 0;
        }
    }
}


}



