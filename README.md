# fastapi-challenge

## Requirements

- [Docker](https://www.docker.com/) (recommended version: 20.10 or higher).
- [Docker Compose](https://docs.docker.com/compose/) (recommended version: 1.29 or higher).

## .env file

This file contains the environment variables needed to run the application. As a template, we have included a .env.example file. Copy this file and rename it to .env. You can customize the database configuration and other environment variables according to your needs. Example values are provided.

## Ports

The application is exposed on port 8000, and the PostgreSQL database on port 5432 (for the application) and 5433 (for testing).

## How to run the application

Once you have cloned the repository, run `docker-compose build` in the root directory of the project and then `docker-compose up`. If you don’t want to see the output in the terminal and prefer to run in the background, you can execute `docker-compose up -d`.

## Tests

You can run tests with `docker-compose run test`


## About the counters

The three implemented counters (create_user_counter, list_users_counter, and background_counter) are in-memory variables, not persistent; therefore, if the server stops, they will reset to 0 upon restarting. Another consequence of this is that if we have more than one instance running in production, each will have different counter values depending on the demand. If persistence of the counters is desired, they could be stored in a database. In any case, the events that increase the counters are logged in the app's log (app/app.log). 
It should also be noted that we consider total calls to /create_user and /list_users, including those made by unauthenticated or unauthorized users.