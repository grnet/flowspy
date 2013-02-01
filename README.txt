===========
1. Tool requirements
Note: Depending on your setup each of the following
may depend on other packages

* python-django
* python-django-extensions
* python-mysqldb
* mysql-client-5.1
* python-gevent
* python-django-south
* python-django-celery
* python-yaml
* python-paramiko (>= 1.7.7.1)
* python-memcache
* python-django-registration
* ncclient (http://ncclient.grnet.gr/,  http://github.com/leopoul/ncclient)
* nxpy (https://code.grnet.gr/projects/nxpy)
* python-lxml
* python-ipaddr
* python-django-tinymce
* apache2
* apache2-mod-proxy
* apache2-mod-rewrite
* apache2-shibboleth : The server should be setup as a Shibboleth SP
* The tool requires an event supporting web server. It is suggested to deploy gunicorn
* If you wish to link your own db tables (peers, networks, etc) with the tool, prefer MySQL MyISAM db engine and use views.

===========
2. Tool architecture

Firewall on Demand applies, via Netconf, flow rules to a network device. These rules are then propagated via e-bgp to peering routers.
Each user is authenticated against shibboleth. Authorization is performed via a combination of a Shibboleth attribute and the peer network
address range that the user originates from.
Components roles:
	- web server (gunicorn): server the tool to localhost:port and allows for events
	- memcached: Caches devices information and aids in syncing
	- gunicorn/beanstalk: Job queue that applies firewall rules in a serial manner to avoid locks

===========
3. Operational requirements

* Shibboleth authentication
    - Shibboleth attributes:
        - eduPersonPrincipalName: Provides a string that uniquely identifies an administrator in the management application.
		- eduPersonEntitlement: A specific URN value must be provided to authorize an administrator: urn:mace:grnet.gr:fod:admin
		- mail: The e-mail address (one or more) of the administrator. It is used for notifications from the management application. It may also be used for further communication, with prior consent.
		- givenName (optional): The person's first name.
		- sn (optional): The person's last name.
		
===========
4. Installation Procedure

4.1 Pre-installation
Configure and setup celeryd, memcached, beanstalkd, web server (gunicorn mode: django), apache
Copy settings.py.dist to settings.py and urls.py.dist to urls.py.
In settings.py set the following according to your configuration:
* DATABASES (to point to your local database). You could use views instead of tables for models: peer, peercontacts, peernetworks. For this to work we suggest MySQL with MyISAM db engine
* STATIC_URL (static media directory) 
* TEMPLATE_DIRS
* CACHE_BACKEND
* NETCONF_DEVICE (tested with Juniper EX4200 but any BGP enabled Juniper should work)
* NETCONF_USER (enable ssh and netconf on device)
* NETCONF_PASS
* BROKER_HOST (beanstalk host)
* BROKER_PORT (beanstalk port)
* SERVER_EMAIL
* EMAIL_SUBJECT_PREFIX
* BROKER_URL (beanstalk url)
* SHIB_AUTH_ENTITLEMENT (if you go for Shibboleth authentication)
* NOTIFY_ADMIN_MAILS (bcc mail addresses)
* PROTECTED_SUBNETS (subnets for which source or destination address will prevent rule creation and notify the NOTIFY_ADMIN_MAILS)
* PRIMARY_WHOIS
* ALTERNATE_WHOIS

4.2 Branding

4.2.1 Logos

Inside the static folder you will find two empty png files: fod_logo.xcf (Gimp file) and shib_login.dist.png.
Edit those two with your favourite image processing software and save them as fod_logo.png (under static/img/) and shib_login.png (under static/). Image sizes are optimized to operate without any
other code changes. In case you want to incorporate images of different sizes you have to fine tune css and/or html as well.

4.2.2 Footer

Under the templates folder (templates), you can alter the footer.html file to include your own footer messages, badges, etc.

4.2.3 Welcome Page

Under the templates folder (templates), you can alter the welcome page - welcome.html with your own images, carousel, videos, etc.

4.3 Configuration Examples

* Gunicorn configuration
	/etc/gunicorn.d/project:
	CONFIG = {
    'mode': 'django',
    'working_dir': '/path/to/flowspy',
   #'python': '/usr/bin/python',
    'args': (
        '--bind=localhost:port',
        '--workers=1',
        '--timeout=360',
        #'--keepalive=90',
        '--worker-class=egg:gunicorn#gevent',
        '--log-level=debug',
        '--log-file=/path/to/fod.log',
        'settings.py',
    ),
}
	
* Apache operates as a gunicorn Proxy with WSGI and Shibboleth modules enabled.
Depending on the setup the apache configuration may vary.
 

* Celeryd example configuration:
	/etc/default/celeryd:
	# Name of nodes to start, here we have a single node
	CELERYD_NODES="w1"
	# or we could have three nodes:
	#CELERYD_NODES="w1 w2 w3"
	
	# Where to chdir at start.
	CELERYD_CHDIR="/path/to/flowspy/"
	# How to call "manage.py celeryd_multi"
	CELERYD_MULTI="$CELERYD_CHDIR/manage.py celeryd_multi"
	
	# How to call "manage.py celeryctl"
	CELERYCTL="$CELERYD_CHDIR/manage.py celeryctl"
	
	# Extra arguments to celeryd
	#CELERYD_OPTS="--time-limit=300 --concurrency=8"
	CELERYD_OPTS="-E -B"
	# Name of the celery config module.
	CELERY_CONFIG_MODULE="celeryconfig"
	
	# %n will be replaced with the nodename.
	CELERYD_LOG_FILE="$CELERYD_CHDIR/celery_var/log/celery/%n.log"
	CELERYD_PID_FILE="$CELERYD_CHDIR/celery_var/run/celery/%n.pid"
	
	# Workers should run as an unprivileged user.
	CELERYD_USER="user"
	CELERYD_GROUP="usergroup"
	
	# Name of the projects settings module.
	export DJANGO_SETTINGS_MODULE="settings"
                                           

4.4 Installation

* Run:
	./manage.py syncdb
	to create all the necessary tables in the database. Enable the admin account to insert initial data for peers and their contact info.
* Then to allow for south migrations:
	./manage.py migration
* Only if you wish to obtain info for your peers from a whois server:
  If you have properly set the primary and alternate whois servers you could go for:
	./manage.py fetch_networks
	to automatically fill network info.
	Alternatively you could fill those info manually via the admin interface.
* Via the admin interface, modify as required the existing (example.com) Site instance
* Modify flatpages to suit your needs 
* Once Apache proxying and shibboleth modules are properly setup, login to the tool. If shibboleth SP is properly setup you should see a user pending activation message and an activation email should arrive at the NOTIFY_ADMIN_MAILS accounts. 


** To share ideas and ask questions drop an email at: leopoul-at-noc(dot)grnet{dot}gr

