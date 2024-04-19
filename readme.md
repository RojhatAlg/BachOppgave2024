3rd party programs needed for this task: <br>
-Python <br>
-Git <br>
-Docker desktop <br>
-Coding IDE

Libraries needed for the program to run:
```
pip install psycopg2
pip install pydriller
```

To initiate the project, execute the following Docker commands in the root directory via the terminal:
```
docker-compose up -d --build
docker-compose up -d
```

Navigate to ``Localhost:8080`` to access the PostgreSQL database. <br> Log in using the password:```password```.

Next, right-click on 'servers' and select 'new server'. Provide a name for the server, such as 'test-server'.

Complete the connection details as follows:

-The hostname to be ```postgres```. <br>
-Username: ``root`` <br> -Password: ``password`` <br> -Finally click 'connect' to establish the server.

With the server now configured, you can access the database. 
Navigate to the database, select the query tool, and proceed to interact with the data.
