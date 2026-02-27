# flux-airflow

## OVERVIEW
This repository serves as the dedicated Airflow codebase for the Flux Data Engineering Team. It is the single source of truth for all DAG definitions running on the Flux Airflow instance deployed on Kubernetes.

All changes to this repository must be made through a Pull Request (PR). Direct pushes to the main branch are strictly blocked. This process ensures full visibility into all workflow changes and deployments. Each PR must be reviewed and approved by an Engineering Lead to ensure workflows are properly designed, optimized, and production-ready before deployment to the Airflow production environment.

## REPOSITORY ARCHITECTURE

<img width="1431" height="663" alt="Screenshot 2026-02-27 at 16 23 31" src="https://github.com/user-attachments/assets/f5442518-de1f-4330-9205-15418a79cc71" />

## REPOSITORY STRUCTURE
`.github/` --->
Contains the CI/CD workflow configurations used for automated testing, building, and deployment.

`business_logic/` --->
Contains reusable business logic modules used by DAG files. DAGs import logic from this directory to maintain clean and modular code.

`config/` --->
Contains Airflow configuration files used for local development. Production Airflow configurations are managed separately in the elite-airflow-values.yaml file.

`plugins/` --->
Contains custom Airflow plugins and shared modules that are not specific to any single DAG. This helps maintain code organization and readability.

`Dockerfile` --->
Defines the Docker image build process used by the CI/CD pipeline to package DAGs and dependencies.

`docker-compose.yaml` --->
Used only for local development and testing. It mirrors the production environment structure, allowing engineers to validate DAGs locally before submitting a Pull Request.

`requirements.txt` --->
Defines the production dependencies required for DAG execution. Add any new libraries here when developing new DAGs.

`requirements-dev.txt` --->
Contains dependencies required only for CI/CD processes, such as testing and validation tools.
