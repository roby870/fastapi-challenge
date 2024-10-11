# fastapi-challenge


# .env file

This file contains the environment variables needed to run the application. As a template, we have included a .env.example file. You should copy this file and rename it to .env, then fill it in with the appropriate values for your system. Example values are provided.


# About the counters

The three implemented counters (create_user_counter, list_users_counter, and background_counter) are in-memory variables, not persistent; therefore, if the server stops, they will reset to 0 upon restarting. Another consequence of this is that if we have more than one instance running in production, each will have different counter values depending on the demand. If persistence of the counters is desired, they could be stored in a database. In any case, the events that increase the counters are logged in the app's log (app/app.log). 
It should also be noted that we consider total calls to /create_user and /list_users, including those made by unauthenticated or unauthorized users.