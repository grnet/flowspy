The following document describes the installation process of Firewall On Demand
on a redhat 6.5 machine with linux 2.6.32-431.17.1.el6.x86_64.

## Step 1: Installing Requirements
The system must have the following packages installed in order for fod to work:

	yum install python-pip libmysqlclient-dev mysql-devel git python-setuptools gcc mysql-devel.x84_64 python-devel libevent-devel libxslt-devel libxml2-devel mysql-server memcached httpd mod_ssl beanstalkd

Then, the next step is to install specific python packages for fod. These packages can be installed via pip (python package manager):



	pip install Django==1.4.5 MySQL-python==1.2.3 PyYAML==3.10 South==0.7.5 amqplib==1.0.2 anyjson==0.3.1 argparse==1.2.1 celery==2.5.3 cl==0.0.3 django-celery==2.5.5 django-picklefield==0.2.1 django-registration==0.8 django-tinymce==1.5 gevent==0.13.6 greenlet==0.3.1 gunicorn==0.14.5 ipaddr==2.1.10 kombu==2.1.8 lxml==3.4.2 mailer==0.7 ncclient==0.4.3 paramiko==1.7.7.1 pycrypto==2.6 pyparsing==1.5.6 python-dateutil==1.5 python-memcached==1.48 wsgiref==0.1.2


`Important!`
There is one package that does not exist in pypi. Its name is Nxpy.
One can install nxpy from the official GRNETs code repository with the following command:

	pip install git+https://code.grnet.gr/git/nxpy

## Step2: Configuring Requirements
FoD Requires the following components to be set up and configured before the installation of FoD:

- Mysql
- A router with flowspec enabled and a user with rw permissions to flowspec and netconf access (port 830) to the device.

For now only mysql can be configured:
### Mysql
In order to configure mysql one has to type the following commands:

	# service mysqld restart
	# mysqladmin -u <user> password <type_a_strong_password>
	# mysql -u root -p
	> CREATE DATABASE fod;
	> exit

After this action the database will accept connections to database `fod` from the root user with the password you typed above.

### Router
Configuring the router in order to accept connections via netconf for a specific user is mentioned just for the sake of completeness.

## Step3: Actuall Installation of FoD

### Downloading and installing
You can download Fod v1.1.1 from GRNETs github repository. Then you have to unzip the file and place it under /srv.

	# cd /tmp
	# wget https://github.com/grnet/flowspy/archive/v1.1.1.zip
	# unzip v1.1.1.zip
	# mv flowspy-1.1.1 /srv/flowspy/

### Additional directory creations
We have to create manually the root directory for the logs:

	mkdir /var/log/fod
	chown apache:apache /var/log/fod


## Step4: Patching files for RedHat
We have noticed that some changes must be made for FoD to work under RedHat.

### Patch the `manage.py` file
We have to change `/srv/flowspy/manage.py` file, and make it look like this:

	import os
	import sys

	if __name__ == "__main__":
    	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flowspy.settings")
	    from gevent import monkey
    	if not 'celery' in sys.argv and not 'celeryd' in sys.argv:
        	monkey.patch_all()

	    from django.core.management import execute_from_command_line

    	execute_from_command_line(sys.argv)

Actually we have just added three new lines of code, but make sure the `manage.py` file looks like this.


### Patch python-tinymce:
We now have to fix a bug from a python package in order to get FoD up and running.
Open

	/usr/lib/python2.6/site-packages/tinymce/widgets.py

you have to replace:

	from django.forms.util import smart_unicode
to

	from django.utils.encoding import smart_unicode

### Syncing the database
To create all the tables needed by FoD we have to run the following commands:

	cd /srv/flowspy
	./manage.py syncdb --noinput
	./manage.py migrate

### Creating a superuser
A superuser can be added by using the following command from `/srv/flowspy/`:

	./manage.py createsuperuser

### Adding some default data
Into `/srv/flowspy` you will notice that there is a directory called `initial_data`. In there, there is a file called `fixtures_manual.xml` which contains some default static pages for django's flatpages app. In this file we have placed 4 flatpages (2 for Greek, 2 for English) with Information and Terms of Service about the service. To import the flatpages, run from `/srv/flowspy`:

	./manage.py loaddata initial_data/fixtures_manual.xml

#### Default Application Site:
Django uses the [Sites Framework](https://docs.djangoproject.com/en/1.4/ref/contrib/sites/) and needs at least a site declared in the database in order to work. So we have to enter the required data in the db. To do that we have to create a file called `sites.json` under `/srv/flowspy/initial_data/`. This file should contain:

	[
    	{
        	"pk": 1,
        	"model": "sites.site",
        	"fields": {
            	"domain": "my-domain.com",
            	"name": "my-domain.com" # its a display name for the domain
        	}
    	}
	]

so please enter the name of the domain you would like. Then load the contents of this file to the database:

	./manage.py loaddata initial_data/sites.json

Its crucial to load this file and load it to the database cause it wont work otherwise.

## Step5: Configuring all the other dependencies

### Beanstalkd
Just start beanstalk already!

	service beanstalkd start


### Celery
Celery is a distributed task queue, which helps FoD run some async tasks, like applying a flowspec rule to a router.

`Note` In order to check if celery runs or even debug it, you can run:

	./manage.py celeryd --loglevel=debug


#### Celery daemon
In order to be able to run celery as a daemon you have to create the celeryd daemon at /etc/init.d/celeryd if it does not already exist:

	vim /etc/init.d/celeryd

The configuration should be:

	#!/bin/sh -e
	# ============================================
	#  celeryd - Starts the Celery worker daemon.
	# ============================================
	#
	# :Usage: /etc/init.d/celeryd {start|stop|force-reload|restart|try-restart|status}
	# :Configuration file: /etc/default/celeryd
	#
	# See http://docs.celeryq.org/en/latest/cookbook/daemonizing.html#init-script-celeryd


	### BEGIN INIT INFO
	# Provides:              celeryd
	# Required-Start:     $network $local_fs $remote_fs
	# Required-Stop:       $network $local_fs $remote_fs
	# Default-Start:       2 3 4 5
	# Default-Stop:        0 1 6
	# Short-Description: celery task worker daemon
	# Description:          Starts the Celery worker daemon for a single project.
	### END INIT INFO

	#set -e

	DEFAULT_PID_FILE="/var/run/celery/%n.pid"
	DEFAULT_LOG_FILE="/var/log/celery/%n.log"
	DEFAULT_LOG_LEVEL="INFO"
	DEFAULT_NODES="celery"
	DEFAULT_CELERYD="-m celery.bin.celeryd_detach"
	ENABLED="false"

	[ -r "$CELERY_DEFAULTS" ] && . "$CELERY_DEFAULTS"

	[ -r /etc/default/celeryd ] && . /etc/default/celeryd

	if [ "$ENABLED" != "true" ]; then
	      echo "celery daemon disabled - see /etc/default/celeryd."
	      exit 0
	fi


	CELERYD_PID_FILE=${CELERYD_PID_FILE:-${CELERYD_PIDFILE:-$DEFAULT_PID_FILE}}
	CELERYD_LOG_FILE=${CELERYD_LOG_FILE:-${CELERYD_LOGFILE:-$DEFAULT_LOG_FILE}}
	CELERYD_LOG_LEVEL=${CELERYD_LOG_LEVEL:-${CELERYD_LOGLEVEL:-$DEFAULT_LOG_LEVEL}}
	CELERYD_MULTI=${CELERYD_MULTI:-"celeryd-multi"}
	CELERYD=${CELERYD:-$DEFAULT_CELERYD}
	CELERYCTL=${CELERYCTL:="celeryctl"}
	CELERYD_NODES=${CELERYD_NODES:-$DEFAULT_NODES}

	export CELERY_LOADER

	if [ -n "$2" ]; then
	      CELERYD_OPTS="$CELERYD_OPTS $2"
	fi

	CELERYD_LOG_DIR=`dirname $CELERYD_LOG_FILE`
	CELERYD_PID_DIR=`dirname $CELERYD_PID_FILE`
	if [ ! -d "$CELERYD_LOG_DIR" ]; then
	      mkdir -p $CELERYD_LOG_DIR
	fi
	if [ ! -d "$CELERYD_PID_DIR" ]; then
	      mkdir -p $CELERYD_PID_DIR
	fi

	# Extra start-stop-daemon options, like user/group.
	if [ -n "$CELERYD_USER" ]; then
	      DAEMON_OPTS="$DAEMON_OPTS --uid=$CELERYD_USER"
	      chown "$CELERYD_USER" $CELERYD_LOG_DIR $CELERYD_PID_DIR
	fi
	if [ -n "$CELERYD_GROUP" ]; then
	      DAEMON_OPTS="$DAEMON_OPTS --gid=$CELERYD_GROUP"
	      chgrp "$CELERYD_GROUP" $CELERYD_LOG_DIR $CELERYD_PID_DIR
	fi

	if [ -n "$CELERYD_CHDIR" ]; then
	      DAEMON_OPTS="$DAEMON_OPTS --workdir=\"$CELERYD_CHDIR\""
	fi


	check_dev_null() {
	      if [ ! -c /dev/null ]; then
	           echo "/dev/null is not a character device!"
	           exit 1
	      fi
	}


	export PATH="${PATH:+$PATH:}/usr/sbin:/sbin"


	stop_workers () {
	      $CELERYD_MULTI stop $CELERYD_NODES --pidfile="$CELERYD_PID_FILE"
	}


	start_workers () {
	      $CELERYD_MULTI start $CELERYD_NODES $DAEMON_OPTS           \
	                                    --pidfile="$CELERYD_PID_FILE"        \
	                                    --logfile="$CELERYD_LOG_FILE"        \
	                                    --loglevel="$CELERYD_LOG_LEVEL"     \
	                                    --cmd="$CELERYD"                           \
	                                    $CELERYD_OPTS
	}


	restart_workers () {
	      $CELERYD_MULTI restart $CELERYD_NODES $DAEMON_OPTS        \
	                                       --pidfile="$CELERYD_PID_FILE"     \
	                                       --logfile="$CELERYD_LOG_FILE"     \
	                                       --loglevel="$CELERYD_LOG_LEVEL"  \
	                                       --cmd="$CELERYD"                        \
	                                       $CELERYD_OPTS
	}



	case "$1" in
	      start)
	           check_dev_null
	           start_workers
	      ;;

	      stop)
	           check_dev_null
	           stop_workers
	      ;;

	      reload|force-reload)
	           echo "Use restart"
	      ;;

	      status)
	           $CELERYCTL status $CELERYCTL_OPTS
	      ;;

	      restart)
	           check_dev_null
	           restart_workers
	      ;;

	      try-restart)
	           check_dev_null
	           restart_workers
	      ;;

	      *)
	           echo "Usage: /etc/init.d/celeryd {start|stop|restart|try-restart|kill}"
	           exit 1
	      ;;
	esac

	exit 0

#### Configuring Celeryd
Celeryd requires a /etc/default/celeryd file to be in place. Thus we are going to create this file (/etc/default/celeryd):

	vim /etc/default/celeryd
The configuration should be

	# Default: false
	ENABLED="true"

	# Name of nodes to start, here we have a single node
	CELERYD_NODES="w1"
	# or we could have three nodes:
	#CELERYD_NODES="w1 w2 w3"

	# Where to chdir at start.
	CELERYD_CHDIR="/srv/flowspy"
	# How to call "manage.py celeryd_multi"
	CELERYD_MULTI="python $CELERYD_CHDIR/manage.py celeryd_multi"

	# How to call "manage.py celeryctl"
	CELERYCTL="python $CELERYD_CHDIR/manage.py celeryctl"

	# Extra arguments to celeryd
	#CELERYD_OPTS="--time-limit=300 --concurrency=8"
	CELERYD_OPTS="-E -B --schedule=/var/run/celery/celerybeat-schedule --concurrency=1 --soft-time-limit=180 --time-limit=1800"
	# Name of the celery config module.
	CELERY_CONFIG_MODULE="celeryconfig"

	# %n will be replaced with the nodename.
	CELERYD_LOG_FILE="/var/log/celery/fod_%n.log"
	CELERYD_PID_FILE="/var/run/celery/%n.pid"

	CELERYD_USER="root"
	CELERYD_GROUP="root"

	# Name of the projects settings module.
	export DJANGO_SETTINGS_MODULE="flowspy.settings"


### Apache (Httpd)
Apache proxies gunicorn. Things are more flexible here as you may follow your own configuration and conventions.

#### Sites enabled
Add this line at the bottom of `/etc/httpd/conf/httpd.conf`

	include sites_enabled

Create the directory `sites_enabled` under `/etc/httpd/` and create and edit `/etc/httpd/sites-enabled/flowspy.conf`. You should set <server_name> and <admin_mail> along with your certificates. If under testing environment, you can use the provided snakeoil certs. If you do not intent to use Shibboleth delete or comment the corresponding configuration parts inside Shibboleth configuration.

	<VirtualHost *:80>
	    ServerName fod.example.org
	    DocumentRoot /var/www
	    ErrorLog /var/log/httpd/fod_error.log
	    LogLevel debug
	    CustomLog /var/log/httpd/fod_access.log combined
	    RewriteEngine On
	    RewriteRule ^/(.*) https://fod.example.com/$1 [L,R]
	</VirtualHost>


	<VirtualHost *:443>
	    SSLEngine on
	    SSLProtocol TLSv1

	    SSLCertificateFile /home/local/GEANT/dante.spatharas/filename.crt
	    SSLCertificateKeyFile /home/local/GEANT/dante.spatharas/filename.key
	    SSLCACertificateFile /home/local/GEANT/dante.spatharas/filename.crt


	    Alias                   /static         /srv/flowspy/static

	    AddDefaultCharset   UTF-8
	    IndexOptions        +Charset=UTF-8

	    #SSLProxyEngine        off
	    ProxyErrorOverride    off
	    ProxyTimeout    28800
	    ProxyPass       /static !
	    ProxyPass        / http://localhost:8080/ retry=0
	    ProxyPassReverse / http://localhost:8080/

	</VirtualHost>

`Important!` You have to comment out/disable the default `Virtualhost` defined on line 74 until the end of this block at `/etc/httpd/conf.d/ssl.conf `.


### Gunicorn
In order for Gunicorn to work properly, you have to create `/etc/init.d/gunicorn` with the following content:

	#!/bin/sh

	### BEGIN INIT INFO
	# Provides: gunicorn
	# Required-Start: $all
	# Required-Stop: $all
	# Default-Start: 2 3 4 5
	# Default-Stop: 0 1 6
	# Short-Description: starts the gunicorn server
	# Description: starts gunicorn using start-stop-daemon
	### END INIT INFO

	# Gunicorn init.d script for redhat/centos
	# Written originally by Wojtek 'suda' Siudzinski <admin@suda.pl>
	# Adapted to redhat/centos by Daniel Lemos <xspager@gmail.com>
	# Gist: https://gist.github.com/1511911
	# Original: https://gist.github.com/748450
	#
	# Sample config (/etc/gunicorn/gunicorn.conf):
	#
	# SERVERS=(
	#  'server_name socket_or_url project_path number_of_workers'
	# )
	#RUN_AS='apache'
	RUN_AS='root'
	#
	# WARNING: user $RUN_AS must have +w on /var/run/gunicorn
	PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
	DAEMON=/usr/bin/gunicorn_django
	LOGGING=--debug
	NAME=flowspy
	DESC=gunicorn
	SERVER="$2"

	test -x $DAEMON || exit 0

	# Source function library.
	. /etc/rc.d/init.d/functions

	# Source networking configuration.
	. /etc/sysconfig/network

	# Check that networking is up.
	[ "$NETWORKING" = "no" ] && exit 0

	if [ -f /etc/gunicorn.d ] ; then
	. /etc/gunicorn.d/*
	fi

	if [ ! -d /var/run/gunicorn ]; then
	mkdir /var/run/gunicorn
	fi

	start () {
	daemon --user $RUN_AS --pidfile /var/run/gunicorn/${data[0]}.pid $DAEMON /srv/flowspy $LOGGING -b 127.0.0.1:8080 -D -p /var/run/gunicorn/${data[0]}.pid --limit-request-fields=10000
	return
	}

	stop () {
	if [ -f /var/run/gunicorn/${data[0]}.pid ]; then
	echo "Killing ${data[0]}"
	kill $(cat /var/run/gunicorn/${data[0]}.pid)
	fi
	}

	case "$1" in
	start)
	echo "Starting $DESC"
	start
	;;
	stop)
	echo "Stopping $DESC"
	stop
	;;
	restart)
	echo "Restarting $DESC"
	stop
	sleep 1
	start
	;;
	*)
	N=/etc/init.d/$NAME
	echo "Usage: $N {start|stop|restart} [particular_server_to_restart]" >&2
	exit 1
	;;
	esac

	exit 0
