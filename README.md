# Fantasy Soccer Manager

This application uses micro-services architecture. Here is the list of different
services we use in dev environment:

- *Django* - This serves the API.
- *PostgreSQL* - The DB service.
- *Cache* - Memcached service for caching data.
- *Celery* - This is for background task management.
- *Rabbitmq* - This is the brocker used by Celery.

For production, we have the following services:

- *Nginx* - This is used as reverse proxy.
- *Gunicorn/Django* - This is the application server. It runs the Python Django
  application.
- *PostgreSQL* - The DB service.
- *Cache* - Memcached service for caching data.
- *Celery* - This is for background task management.
- *Rabbitmq* - This is the brocker used by Celery.

## Installation
The easiest way to start development is through Docker setup. If you have
Docker, run the following command to setup everything:

```
docker-compose build
docker-compose up -d
```

You can access the application at http://localhost:8000/


## Fake Data and Simulation
When you run the application in development environment, you can expect the
following users in the DB:
- **Superadmin** - Creds: admin@example.com/admin
- **User** - Creds: owner@example.com/soccer
- **Default User** - Creds: signup@example.com/soccer


## Production Deployment
Production deployment is also done using Docker. All the files associated with
prod deployment are present in prod folder. To start prod build, do:

```
cd prod
docker-compose build
docker-compose up -d
````

## Linters
This project uses following linters:

- GitLint: This is used to maintain quality of Git commit messages.
- Flake8: This is used to maintain quality of Python code.
- Isort: This is used to maintain imports in Python files.

To run run all linters, do:

```
docker-compose exec api bash
./scripts/lint.sh
```

You can fix Isort issues by running the following command:

```
docker-compose exec api bash
isort <file path>
```

## Configuration files
There are multiple special files that are actively used by this project:

- .isort.cfg: This file is used to configure ISort.
- .gitignore: This file is used to ignore files in Git.
- .gitlab-ci.yml: This file is used to configure CI.
- .dockerignore: This file is used to ignore files from Docker context.
- .flake8: Thiis file is used to configuration Flake8.
- .gitlint: This file is used to configure GitLint.
- .coveragerc: This is file is used to configure coverage options.

## Testing
You can run tests with the following command:

```
docker-compose exec api bash
./scripts/test.sh
```

You can run tests with coverage with the following command:

```
docker-compose exec api bash
./scripts/test-with-coverage.sh
```

## Debugging
This project integrates Django Debug Toolbar. It is a very good tool to profile
the API code. As a note, you should always try to improve performance
bottlenecks after profiling your code. You can see the toolbar, by logging in
with the superuser and then sending debug=true query parameter in the URL. For
example:

```
http://localhost:8000/users/?debug=true
```

## Documentation
You can access very detailed Swagger based documentation by accessing:

```
http://localhost:8000/docs/
```

## Permission Levels
There are 4 permission levels in this application:

1. *Unauthed* - When we don't send an auth token.
2. *Default* - When we send auth token, but this auth token is associated to a
   default user. This user is not a real user. The purpose is to not provide
   public access of this API.
3. *Authed* - We send auth token belonging to a real user.
   admin.
4. *Admin* - We send auth token belonging to admins. This has unrestricted
   access to APIs.
