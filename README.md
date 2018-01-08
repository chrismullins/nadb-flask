[![Build Status](https://travis-ci.org/chrismullins/flask-microservices-users.svg?branch=master)](https://travis-ci.org/chrismullins/flask-microservices-users)

### Run the tests:
* Create the venv:
```bash
python -m venv venv/
source venv/bin/activate
pip install -r requirements.txt
```
* Set the environment variables
```bash
export DATABASE_URL=postgres://postgres:postgres@localhost:5432/nailart_db
export SECRET_KEY="my_precious"
export APP_SETTINGS=project.config.DevelopmentConfig
# and if you want to run the tests...
export DATABASE_TEST_URL=postgres://postgres:postgres@localhost:5432/nailart_db_test
```
* Run the tests:
```bash
python manage.py test
```