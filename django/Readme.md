# Django
## Run makemigrations and migrate
Migrations are how Django stores changes to your models. To do this, from the command line, run the following command, where "app-name" is a Django's application name.

```bash
python manage.py makemigrations app-name
# ex.
# python manage.py makemigrations sns
```

By running makemigrations, you're telling Django that you've made some changes to your models and that you'd like the chages to be stored as a migration.

There's a command that will run the migrations for you and manage your database schema automatically - that's called migrate.
Now, run migrate to create your model tables in your database.

```bash
python manage.py migrate
```

Please remember the tree-step guid to making model changes:
1. Change your models (in models.py).
1. Run `python manage.py makemigrations app-name` to create migrations for those changes in your application.
1. Run `python manage.py migrate` to apply those changes to the database.

## Create superuser account
To create superuser account, let's run following command, where `DJANGO_SUPERUSER_NAME`, `DJANGO_SUPERUSER_EMAIL`, and `DJANGO_SUPERUSER_PASSWORD` are environment variables
defined by `env_file/django/.env`.

```bash
python manage.py custom_createsuperuser \
                 --username ${DJANGO_SUPERUSER_NAME} \
                 --email ${DJANGO_SUPERUSER_EMAIL} \
                 --password ${DJANGO_SUPERUSER_PASSWORD}
```

## Create multilingual localization messages
```bash
django-admin.py makemessages -l ja
# edit .po files
django-admin.py compilemessages
```

## Set Time Zone for AXES
In MySQL container, let's run following command to set time zone.

```bash
mysql_tzinfo_to_sql /usr/share/zoneinfo | mysql -D mysql -u root -proot_password # Must not set space between "-p" and "root_password".
#
# please wait for few minutes ...
#
mysql -u root -proot_password -e "flush tables;" mysql # if this command succeeded, no message is displayed.
```
