![AI-Annotator](docs/figs/logo.png)
*Free web-based data labeling software designed for a wide range of AI projects.*

# Instalation
> [!NOTE]
> To be able to use the software, make sure you have [`docker-compose`](https://docs.docker.com/compose/) installed on your machine.

1. Configure the `.env` file based on the `.env.example`. This file contains some of the necessary enviroment variables to set up the software.
2. Install and set up all containers.
```bash
bash ai-annotator.sh -i
```
3. Run the software.
```bash
bash ai-annotator.sh -r
```

You can use the following commands to manage the application as well:
```bash
bash ai-annotator.sh -s # Stop the software.
bash ai-annotator.sh -c # Clear and reset the software.
```

## Manual deployment
If the `ai-annotator.sh` does not work correctly on your machine, you can run manually all commands to deploy the software if you want.
```
docker compose --profile app build -q # Install/Set up software.
docker compose --profile app up -d # Run the software.
docker compose --profile app down # Stop the software.
docker compose --profile app down --rmi all -v --remove-orphans 2>/dev/null || true # Clear and reset the software.
```
