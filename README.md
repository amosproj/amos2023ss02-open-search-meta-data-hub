# OpenSearch Metadata-Hub

<p align="center">
  <img src="./Deliverables/sprint-01/team-logo.png" alt="" width="300"/>
</p>

## Start

Here, you can learn, how to start the OpenSearch-Metadata-Hub.

1) Install [Docker](https://docs.docker.com/desktop/).
2) Start "Docker Desktop" on your machine.
3) Go to [our repository](https://github.com/amosproj/amos2023ss02-open-search-meta-data-hub) and download the latest release of this project: ![image](https://github.com/amosproj/amos2023ss02-open-search-meta-data-hub/assets/105235679/1e809ffd-c11d-4c42-bd0f-a667ae1c3992)
4) Create a `.env`-file. It should contain key-value-pairs for `URL_CORE_1` and `PW_USER_CORE_1`, where you can store your credentials. Here is an example, how the contents should look like:
```
URL_CORE_1=https://metadahub.de/example
PW_USER_CORE_1=testpw
```
5) Navigate to the `src/`-folder and execute `docker compose up`. Alternatively, you can also execute `docker compose up -d` for detached mode.
6) Our website runs on port 8000, so you should be able to access it on [localhost:8000](localhost:8000).
7) Top stop all services, run `docker compose down` in `src/`.
8) You can use the `-v`-option in the last command to clear persistent data (e.g. to clear imported data). This action cannot be undone!
