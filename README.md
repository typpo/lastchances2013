13lastChances
=============

#2013 Last Chances

Flask App for matching seniors with each other during 13S, uses dnd-ldap library from [here](https://github.com/DartmouthHackerClub/blitzlistr-flask), and hosts data on mongo database at MongoHQ.com

##Setup
Assuming you have python and pip install, install virtualenv:
```python
$ sudo pip install virtualenv
$ virtualenv venv
$ source venv/bin/activate
```

You are now in the isolated venv environment. To install all required modules/libraries, run:
```python
$ pip install -r requirements.txt
 ```
##Usage
Once you have completed the above steps, you can run the app using:
```python
$ python app.py
```

You can also write to the DB directly from the shell using:
```python
$ python manage.py shell
```

NOTE: For all this to work you need to set the global environment variable MONGOHQ_URL to point to the DB online. Get in touch with me directly if you want this URL.


