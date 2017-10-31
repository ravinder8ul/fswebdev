# Project: Logs Analysis
### Purpose of this project
To build an internal reporting tool that will use information from the database to discover what kind of articles the site's readers like
1. What are the most popular three articles of all time?
2. Who are the most popular article authors of all time?
3. On which days did more than 1% of requests lead to errors?

### Project environment setup
1. Python 2
2. psycopg2 library, and
3. An up-and-running PostgreSQL environment, [ follow these instruction ][1]
4. Download the [ newsdata.sql ][2] file
5. To load the data, cd into the vagrant directory and use the command **psql -d news -f newsdata.sql**

### Running the project
In order to run the code first download the source code to your local machine.
Put the reportingtool.py python file under the vagrant folder after logging into
vagrant box

Run the program as:
```
python reportingtool.py
```
or as shell executable, file should have +x permission
```
$ ./reportingtool.py
```

[1]: https://classroom.udacity.com/nanodegrees/nd004/parts/8d3e23e1-9ab6-47eb-b4f3-d5dc7ef27bf0/modules/bc51d967-cb21-46f4-90ea-caf73439dc59/lessons/5475ecd6-cfdb-4418-85a2-f2583074c08d/concepts/14c72fe3-e3fe-4959-9c4b-467cf5b7c3a0
[2]: https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip
