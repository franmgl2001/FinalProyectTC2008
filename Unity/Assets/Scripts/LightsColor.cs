/*
This script is used to change the color of the traffic lights. of the traffic lights.
Collaborators:Francisco Martinez Gallardo, Omar Rivera
Date: 2023-11-30
*/

using UnityEngine;

public class LightsColor : MonoBehaviour
{
    public Material greenLightMaterial; // Green light material
    public Material redLightMaterial; // Red light material 
    public Color greenLightColor = Color.green; // Green light color
    public Color redLightColor = Color.red; // Red light color
    public float changeInterval = 5.0f; // Time interval to change the color of the traffic light
    public int state = 0; // State of the traffic light
    private MeshRenderer meshRenderer;// Mesh renderer of the traffic light
    private Light trafficLight;// Light of the traffic light


    void Start()
    {
        // Get the mesh renderer and light component of the traffic light
        meshRenderer = GetComponent<MeshRenderer>();
        trafficLight = GetComponent<Light>();
    }

    void Update()
    {
        if (state == 0)
            {
                meshRenderer.material = redLightMaterial;
                trafficLight.color = redLightColor;
            }
            else
            {
                meshRenderer.material = greenLightMaterial;
                trafficLight.color = greenLightColor;
            }
        }
    }

