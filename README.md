# ddao-web

This is a basic html interface for an Assistant API chatbot.

Set up the virtual environment for the flask api. in the ddao-web/api directory,

run

python3 -m venv .venv

and using python3 -m pip install

requests
redis
Flask-APScheduler
flask

then, run

systemctl start react-flask-app

set up react

npm run build
cp /root/ddao-web/react-flask-app/build/. /var/www/ddao-web
