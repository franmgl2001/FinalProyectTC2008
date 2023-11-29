using UnityEngine;

public class LightsColor : MonoBehaviour
{
    public Material greenLightMaterial; 
    public Material redLightMaterial;   
    public Color greenLightColor = Color.green; 
    public Color redLightColor = Color.red;   
    public float changeInterval = 5.0f;

    private MeshRenderer meshRenderer;
    private Light trafficLight;
    private float timer;
    private bool isGreen = true;

    void Start()
    {
        meshRenderer = GetComponent<MeshRenderer>();
        trafficLight = GetComponent<Light>();

        if (meshRenderer == null)
        {
            Debug.LogError("No MeshRenderer component found on the traffic light object.");
            return;
        }

        if (trafficLight == null)
        {
            Debug.LogError("No Light component found on the traffic light object.");
            return;
        }

        // Comenzar con la luz verde
        meshRenderer.material = greenLightMaterial;
        trafficLight.color = greenLightColor;
        timer = changeInterval;
    }

    void Update()
    {
        timer -= Time.deltaTime;
        if (timer <= 0)
        {
            if (isGreen)
            {
                meshRenderer.material = redLightMaterial;
                trafficLight.color = redLightColor;
            }
            else
            {
                meshRenderer.material = greenLightMaterial;
                trafficLight.color = greenLightColor;
            }
            isGreen = !isGreen;
            timer = changeInterval;
        }
    }
}
