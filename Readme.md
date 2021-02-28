# Multi Web Service (MWS)
## Preparation
Open port 443 of network router used by Nginx.

## Build docker image
First, from the command line, cd into a directory where this Readme.md exists.

Then, run the following command and wait for a few minutes.

```bash
docker-compose build
```

## Create a project
If this is your first time using Django, you'll have to take care of some initial setup.

Namely, you'll need to auto-generate some code that establishes a Django project - a collection of settings for an instance of Django,
including database configuration, Django-specific options and application-specific settings.

From the command line, run the following command:

```bash
# project name is web_service
docker-compose run --rm django django-admin startproject web_service .
```

## Create the SNS app
Now that your environment - a "project" - is set up, you're set to start doing work.

To create your app, cd into the same directory as manage.py and type these commands:

```bash
# app name is registration
docker-compose run --rm django python manage.py startapp registration
# app name is sns
docker-compose run --rm django python manage.py startapp sns
# app name is blog
docker-compose run --rm django python manage.py startapp blog
# delete container with volume
docker-compose down -v
```

## Change the owner
In host machine, run the following command as root:

```
sudo chown ${USER}:${USER} -R ./django/src
```

## Start all docker container
Finally, cd into a directory where this Readme.md exists and type this command:

```bash
docker-compose up -d
```

Let's start development!
