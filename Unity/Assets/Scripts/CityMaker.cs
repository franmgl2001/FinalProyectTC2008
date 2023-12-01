/*
This script is used to create the city layout from a text file.
Collaborators:Gilberto Echeverria, Octavio Navarro, Omar Rivera, Francisco Martinez Gallardo
*/

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CityMaker : MonoBehaviour
{
    [SerializeField] TextAsset layout;
    [SerializeField] GameObject roadPrefab;
    [SerializeField] GameObject[] buildingPrefab;
    [SerializeField] GameObject semaphorePrefab;
    [SerializeField] int tileSize;

    // Start is called before the first frame update
    void Start()
    {
        MakeTiles(layout.text);
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    void MakeTiles(string tiles)
    {
        int x = 0;
        // Mesa has y 0 at the bottom
        // To draw from the top, find the rows of the file
        // and move down
        // Remove the last enter, and one more to start at 0
        int y = tiles.Split('\n').Length -1;
        Debug.Log($"Starting y: {y}");

        Vector3 position;
        GameObject tile;

        for (int i=0; i<tiles.Length; i++) {
            if (tiles[i] == '>' || tiles[i] == '<') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.identity);
                tile.transform.parent = transform;
                x += 1;
            } else if (tiles[i] == 'v' || tiles[i] == '^') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                x += 1;
            } else if (tiles[i] == 's') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.identity);
                tile.transform.parent = transform;
                x += 1;
            } else if (tiles[i] == 'S') {
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(roadPrefab, position, Quaternion.Euler(0, 90, 0));
                tile.transform.parent = transform;
                x += 1;
            } else if (tiles[i] == 'D') {
                int rand= Random.Range(0,buildingPrefab.Length);
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(buildingPrefab[rand], position, Quaternion.Euler(0, 90, 0));
                tile.GetComponent<Renderer>().materials[0].color = Color.red;
                tile.transform.parent = transform;
                x += 1;
            } else if (tiles[i] == 'I') {
            // New condition for handling 'I'
            position = new Vector3(x * tileSize, 0, y * tileSize);
            tile = Instantiate(roadPrefab, position, Quaternion.identity);
            tile.transform.parent = transform;

            // Debug log for the 'I' building
            Debug.Log($"Building ('I') created at x: {x}, y: {y}, position: {position}");

            x += 1; 
            } else if (tiles[i] == '#') {
                int rand= Random.Range(0,buildingPrefab.Length);
                position = new Vector3(x * tileSize, 0, y * tileSize);
                tile = Instantiate(buildingPrefab[rand], position, Quaternion.identity);
                tile.transform.localScale = new Vector3(1, Random.Range(0.5f, 2.0f), 1);
                tile.transform.parent = transform;
                x += 1;
            } else if (tiles[i] == '\n') {
                x = 0;
                y -= 1;
            }
        }

    }
}