# TweetMatch
Do you tweet like Donald Trump? This tool will tell you if you do!
How big is the chance that your tweet is written by the Trump? This tool will show the "Trumpiness &copy;" of your tweet and display it with some amazing graphics.

## Setup
Setting up our webserver requires 3 steps:
1. Create a python environment and install the modules in the requirements.txt file. (this can easily be done by running `virtualenv --no-site-packages --distribute .env && source .env/bin/activate && pip install -r TweetMatch/requirements.txt` just outside of the git directory
2. Place your twitter authentication keys in the working directory from which you'll run the server. See below for creating a valid `keys.dat` file (the model and tweet database will also be saved here).
3. Run the server from the directory in which you want the data to be saved by invoking 'run.py' in `TweetMatch/WebServer` (running the server from 'TweetMatch/WebServer/App/data' with `./../../run.py` will store the data there. Just make sure your keys.dat file is also in this directory)

## Keys.dat
TweetMatch requires a `keys.dat` file with your twitter authentication keys that you have to create yourself. If you already have the tweets in the correct format the webserver will recognize this and skip the downloading step.
The `keys.dat` file should look like this:
```
consumer_key
consumer_secret
access_key
access_secret

```
(note the empty line on the bottom)
The keys can be found on the `apps.twitter.com` website after you create your app. (see the image below)
![alt text](https://raw.githubusercontent.com/Denpeer/TweetMatch/master/images/keys.png "keys on the app.twitter.com website")
