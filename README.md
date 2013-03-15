13lastChances
=============

#2013 Last Chances

Flask App for matching seniors with each other during 13S. Uses dnd-ldap library from [here](https://github.com/DartmouthHackerClub/blitzlistr-flask) for lookups, and hosts data on mongo database at MongoHQ.com

##Setup
Of course, clone the repo first using:

```bash
git clone https://github.com/DartmouthHackerClub/13lastChances.git
```

Assuming you have python and pip installed, install virtualenv and create a new environment:
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
The above will launch the app at the address "localhost:5000"
You will first need to login with your Dartmouth info, then you'll be taken through to a form where you can enter your choices. Hitting 'submit' on the form writes your info to the DB.

If you want to play around, you can write to the DB directly from the shell using:
```python
$ python manage.py shell
```

NOTE: For all this to work you need to set the global environment variable MONGOHQ_URL to point to the DB online. Get in touch with me directly if you want this URL.

##TODO
- Clear browser cookies on logout
- Make nicer CSS stylings
- Fix look-up so that bogus names cannot be submitted
- Add drop-down menu if lookup returns multiple matches

