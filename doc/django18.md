# Django 1.8 Upgrade guide

This document describes the process required to upgrade FLOWSPY to Django 1.8.

## Basic information

### Django versions & support

When this branch is merged on `master` support for pre 1.8 Django versions will
be officially dropped, so it is best to upgrade as soon as possible to continue
receiving the newest features and bug fixes.

### Requirements & Package upgrades

The project's requirements have changed. We are always trying to follow the
Debian releases & official packages but it is not always possible, so some
packages need to be installed by `pip`.

This version has been developed and tested for Debian 8.0 (Jessie)

Versions comparison (changed packages)

| Package name               | Old Version | New Version | Debian Jessie |
|:--------------------------:|:-----------:|:-----------:|:-------------:|
| python-django              | 1.4.5       | 1.8.16      | X (backports) |
| python-django-registration | 0.8         | 2.0.4       | X             |
| python-celery              | 2.5.5       | 3.1.23      | X             |
| python-django-celery       | 2.5.5       |        --   |          --   |
| python-djangorestframework |        --   | 2.4.3       | X             |
| python-django-south        | 0.7.5       |      --     |      --       |
| python-redis               | --          | 2.10.1      | X             |


### A note on `*_MANAGED_TABLE` settings

Settings `PEER_MANAGED_TABLE`, `PEER_RANGE_MANAGED_TABLE`, 
`PEER_TECHC_MANAGED_TABLE` control whether models `Peer`, `PeerRange`
and `TechcEmail` are managed by the Django migration system or not.
It is recommended to leave these options to `True`. These options,
however, allow you to use MySQL views instead of actual tables in case
you want to integrate FLOWSPY with a CRM etc. 

Please note that you should **pick an option during installation** and
stick with it. Changing these options after the app has been deployed
and these tables have actual data is **dangerous** and may lead to 
**data loss**.

The new Django migrations deal with an issue related to these settings.
The previously provided migrations did not take care of skipping MySQL
Foreign Key constraints for tables that might be views. E.g. if 
`Peer` table is actually a view, all `ForeignKey`s referencing this model
should not create database level constraints since these will always fail
(see [gist](https://gist.github.com/grnetnoc/63e8d1cfb9c9e267ca88ce2f675d0ea7)).

## Upgrade procedure

### Pre-upgrade steps

It is always a good idea to take a dump of your database during such operations
to ensure that no data is lost should anything go wrong. This would be the best
time to do so.

To succesfully upgrade to the new version you first need to make sure you have
applied the latest migrations before the upgrade. To do this:

    git pull origin master
    git checkout v1.3.1
    ./manage.py migrate

Then you are ready to upgrade to the latest version.

    git checkout master

### Installation of new packages

Now it is time to install the new packages. You can either install the official
Debian packages

    sudo apt-get install python-django python-django-registration 
    python-djangorestframework

or use pip:

    pip install -r requirements.txt

It is also suggested (but not directly required) to upgrade your `nxpy` & 
`ncclient` versions. To do so, you must install them via pip:

    pip install git+https://code.grnet.gr/git/nxpy  
    pip install ncclient

### Project upgrade

To upgrade:

    ./manage.py migrate

To install `python-celery` you must first ensure that any previous custom
Celery configuration you might have used is no longer present. So:

    sudo rm /etc/defaults/celeryd /etc/defaults/celerybeat
    /etc/defaults/celeryevcam

The new version of the package adds it's own scripts which are sufficient. Then
you can install the package

    sudo apt-get install python-celery

Then you need to make sure that your `settings.py` is up to date with whatever
has changed in `settings.py.dist`. Use

    git diff master..django18upgrade -- flowspy/settings.py.dist

to see the differences and apply them manually.
Then finally,

    ./manage.py collectstatic --noinput

and the upgrade is complete.

## Post upgrade configuration

### Celery using Debian Jessie system package

In production you will probably want to run Celery as a service (using `init.d`)
. To do so, you must update the Celery init.d scripts since Debian Jessie has a
bug:

    /etc/defaults/celeryd:
     
     _chuid () {
    -    su "$CELERYD_USER" -c "$CELERYD_MULTI $*"
    +    su "$CELERYD_USER" --shell=/bin/sh -c "$CELERYD_MULTI $*"
     }

    /etc/default/celerybeat:

Then, you need to update the default Celery config
with your environment specific options.
Some defaults would be:


    /etc/defaults/celeryd:

    # Change this to true when done to enable the init.d script.
    # Default: false
    ENABLED="true"
    
    # Name of nodes to start
    # here we have a single node
    CELERYD_NODES="flowspy"
    # or we could have three nodes:
    # CELERYD_NODES="w1 w2 w3"
    
    # Where to chdir at start.
    CELERYD_CHDIR="<your-deployment-directory>"
    CELERY_APP="flowspy"
    
    # Extra arguments to celeryd
    CELERYD_OPTS="--time-limit=300 --concurrency=2"
    
    # %n will be replaced with the nodename.
    CELERYD_LOG_FILE="/var/log/celery/%n.log"
    
    # Workers should run as an unprivileged user.
    CELERYD_USER="<a-user-to-run-celery>"
    CELERYD_GROUP="<a-group>"


    /etc/defaults/celerybeat:
 
    # Default: false
    ENABLED="true"
    
    # Where to chdir at start.
    CELERYBEAT_CHDIR="<your-deployment-directory>"
    
    # Extra arguments to celeryd
    CELERYBEAT_OPTS="--schedule=/var/run/celery/celerybeat-schedule "
    # Name of the celery config module.
    CELERY_CONFIG_MODULE="flowspy"
    
    # Workers should run as an unprivileged user.
    CELERYD_USER="celery"
    CELERYD_GROUP="celery"


Finally, make sure the user has permissions to write to the log files

You can now run celery / celerybeat using

    /etc/init.d/celeryd start
    /etc/init.d/celerybeat start

### Celery running from a virtualenv

Things are quite simple here. Go to the installation directory,
activate your virtualenv and run a celery worker:

    celery -A flowspy worker

To run celerybeat:

    celery -A flowspy beat
