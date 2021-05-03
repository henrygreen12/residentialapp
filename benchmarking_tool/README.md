- Make sure to activate your virtual environment first ("benchmarking_tool" for me), if not create one
- call this command " conda env config vars set FLASKAPP=yourvirtualenv:app
- We need to stay on the root first
- I created a seeds file to run the python data script and the role.py
- I also added the differents property tax assesm
- I moved the weather_edmonton.py in the root
- HERE are the steps :
1- Delete the migration folder in the root
2- Delete the test.db in benchmarking_tool/test.db
3- Still in the root path:
	- flask db init
	- flask db migrate -m "Initial migration"
	- flask db upgrade
	- flask seed run (It's going to create the database and add the roles)
	- python weather_edmonton.py in another terminal action-button

It will create all the data base and the edmonton weather will be on the database every 3600 seconds instead of 10 seconds
