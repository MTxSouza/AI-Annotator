# AI-Annotator
WEB software used to annotate multiple data for a vast AI tasks.

## Run
To build and run the application on your browser, you can simply run the following command:
```bash
$ docker compose up -d
```
This command will build follwing services on your machine (you can visualize them using `docker images`):
|Container|Description|
|-|-|
|**ai-annotator-database**|The MongoDB instance used to store some data of your projects.|
|**ai-annotator-backend**|The main backend API of the application.|