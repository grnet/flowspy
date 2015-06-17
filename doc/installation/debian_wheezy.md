# Debian Wheezy (x64) - Django 1.4.x
The following document describes the installation process of Firewall On Demand
on a Debian Wheezy machine with Django 1.4

## Upgrading

### Upgrading from v<1.1.x

> ** Note **
>
> If PEER\_\*\_TABLE tables are set to FALSE in settings.py, you need to
> perform the south migrations per application:

     ./manage.py migrate longerusername
     ./manage.py migrate flowspec
     ./manage.py migrate accounts

Also, pay attention to settings.py
changes. Also, do not forget to run if PEER\_\*\_TABLE tables are set to
TRUE in settings.py:

    ./manage.py migrate

to catch-up with latest database changes.

### Upgrading from v<1.0.x

If upgrading from flowspy v<1.0.x pay attention to settings.py
changes. Also, do not forget to run:

    ./manage.py migrate

to catch-up with latest database changes.


## Installing from scratch

### Required system packages (with apt)

Update and install the required packages:

    apt-get update
    apt-get upgrade
    apt-get install mysql-server apache2 memcached libapache2-mod-proxy-html gunicorn beanstalkd python-django python-django-south python-django-tinymce tinymce python-mysqldb python-yaml python-memcache python-django-registration python-ipaddr python-lxml mysql-client git python-django-celery python-paramiko python-gevent

Also, django rest framework package is required. In debian Wheezy it is
not available, but one can install it via pip.

> **note**
>
> Set username and password for mysql if used

> **note**
>
> If you wish to deploy an outgoing mail server, now it is time to do
> it. Otherwise you could set FoD to send out mails via a third party
> account

### Create a database

If you are using mysql, you should create a database:

    mysql -u root -p -e 'create database fod'

### Required application packages

Get the required packages and their dependencies and install them:

    apt-get install libxml2-dev libxslt-dev gcc python-dev

-   ncclient: NETCONF python client:

        cd ~
        git clone https://github.com/leopoul/ncclient.git
        cd ncclient
        python setup.py install

-   nxpy: Python Objects from/to XML proxy:

        cd ~
        git clone https://code.grnet.gr/git/nxpy
        cd nxpy
        python setup.py install

- flowspy: core web application. Installation is done at /srv/flowspy::

        cd /srv
        git clone https://code.grnet.gr/git/flowspy
        cd flowspy

Let’s move on with some copies and dir creations:

    mkdir /var/log/fod
    chown www-data.www-data /var/log/fod
    cp urls.py.dist urls.py
    cd ..

## System configuration
Apache operates as a gunicorn Proxy with WSGI and Shibboleth modules
enabled. Depending on the setup the apache configuration may vary:

    a2enmod rewrite
    a2enmod proxy
    a2enmod ssl
    a2enmod proxy_http

If shibboleth is to be used:

    apt-get install libapache2-mod-shib2
    a2enmod shib2

Now it is time to configure beanstalk, gunicorn, celery and apache.

### beanstalkd


Enable beanstalk by editting /etc/default/beanstalkd:

    vim /etc/default/beanstalkd

Uncomment the line **START=yes** to enable beanstalk

Start beanstalkd:

    service beanstalkd start

### gunicorn.d
Create and edit /etc/gunicorn.d/fod:

    vim /etc/gunicorn.d/fod

FoD is served via gunicorn and is then proxied by Apache. If the above
directory conventions have been followed so far, then your configuration
should be:

    CONFIG = {
          'mode': 'django',
          'working_dir': '/srv/flowspy',
          'args': (
               '--bind=127.0.0.1:8081',
               '--workers=1',
               '--worker-class=egg:gunicorn#gevent',
               '--timeout=30',
               '--debug',
               '--log-level=debug',
               '--log-file=/var/log/gunicorn/fod.log',
          ),
    }

### celeryd


Celery is used over beanstalkd to apply firewall rules in a serial
manner so that locks are avoided on the flowspec capable device. In our
setup celery runs via django. That is why the python-django-celery
package was installed.

Create the celeryd daemon at /etc/init.d/celeryd **if it does not
already exist**:

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

#### celeryd configuration
celeryd requires a /etc/default/celeryd file to be in place. Thus we are
going to create this file (/etc/default/celeryd):

    vim /etc/default/celeryd

Again if the directory conventions have been followed the file is (pay
attention to the CELERYD\_USER, CELERYD\_GROUP and change accordingly) :

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

### Apache
Apache proxies gunicorn. Things are more flexible here as you may follow
your own configuration and conventions. Create and edit
/etc/apache2/sites-available/fod. You should set \<server\_name\> and
\<admin\_mail\> along with your certificates. If under testing
environment, you can use the provided snakeoil certs. If you do not
intent to use Shibboleth delete or comment the corresponding
configuration parts inside **Shibboleth configuration** :

    vim /etc/apache2/sites-available/fod

Again if the directory conventions have been followed the file should
be:

    <VirtualHost *:80>
        ServerAdmin webmaster@localhost
        ServerName  fod.example.com
        DocumentRoot /var/www

        ErrorLog ${APACHE_LOG_DIR}/fod_error.log

        # Possible values include: debug, info, notice, warn, error, crit,
        # alert, emerg.
        LogLevel debug

        CustomLog ${APACHE_LOG_DIR}/fod_access.log combined

        RewriteEngine On
        RewriteCond %{HTTPS} off
        RewriteRule ^/(.*) https://fod.example.com/$1 [L,R]
    </VirtualHost>

    <VirtualHost *:443>
        ServerName    fod.example.com
        ServerAdmin     webmaster@localhost
        ServerSignature        On

        SSLEngine on
        SSLCertificateFile    /etc/ssl/certs/fod.example.com.crt
        SSLCertificateChainFile /etc/ssl/certs/example-chain.pem
        SSLCertificateKeyFile    /etc/ssl/private/fod.example.com.key

        AddDefaultCharset UTF-8
        IndexOptions        +Charset=UTF-8

        ShibConfig       /etc/shibboleth/shibboleth2.xml
        Alias          /shibboleth-sp /usr/share/shibboleth


        <Location /login>
             AuthType shibboleth
             ShibRequireSession On
             ShibUseHeaders On
             ShibRequestSetting entityID https://idp.example.com/idp/shibboleth
             require valid-user
        </Location>

        # Shibboleth debugging CGI script
        ScriptAlias /shibboleth/test /usr/lib/cgi-bin/shibtest.cgi
        <Location /shibboleth/test>
             AuthType shibboleth
             ShibRequireSession On
             ShibUseHeaders On
             require valid-user
        </Location>

        <Location /Shibboleth.sso>
             SetHandler shib
        </Location>

        # Shibboleth SP configuration

        #SetEnv                       proxy-sendchunked

              <Proxy *>
               Order allow,deny
               Allow from all
               </Proxy>

               SSLProxyEngine           off
               ProxyErrorOverride     off
          ProxyTimeout     28800
             ProxyPass        /static !
             ProxyPass          /shibboleth !
             ProxyPass        /Shibboleth.sso !

               ProxyPass           / http://localhost:8081/ retry=0
               ProxyPassReverse / http://localhost:8081/

          Alias /static          /srv/flowspy/static

        LogLevel warn

Now, enable your site. You might want to disable the default site if fod
is the only site you host on your server:

    a2dissite default
    a2ensite fod

You are not far away from deploying FoD. When asked for a super user,
create one:

    cd /srv/flowspy
    python manage.py syncdb
    python manage.py migrate longerusername
    python manage.py migrate flowspec
    python manage.py migrate djcelery
    python manage.py migrate accounts
    python manage.py migrate

If you have not changed the values of the PEER\_\*\_TABLE variables to
False and thus you are going for a default installation (that is
PEER\_\*\_TABLE variables are set to True) , then run:

    python manage.py migrate peers

If however you have set the PEER\_\*\_TABLE variables to False and by
accident you have ran the command above, then you have to cleanup you
database manually by dropping the peer\* tables plus the techc\_email
table. For MySQL the command is:

    DROP TABLE `peer`, `peer_networks`, `peer_range`, `peer_techc_emails`, techc_email;

Restart, gunicorn and apache:

    service gunicorn restart && service apache2 restart
