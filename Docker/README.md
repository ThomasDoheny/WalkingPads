## Docker

This Docker setup was tested in Windows. For visualizations to work, MobaXterm must be running in the background as an X server.
To use on Linux/Mac, update the `DISPLAY` environment variables in `Docker/compose.yml` accordingly.

```bash
git clone https://github.com/ThomasDoheny/WalkingPads
cd WalkingPads/Docker
docker compose up -d
docker exec -it walkingpads bash
```

Once inside the container, proceed with instructions from the top level README.
