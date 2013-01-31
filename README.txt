===========
1. Tool requirements

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
* python-ncclient
* python-nxpy
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
    - Required shibboleth attributes:
        - HTTP_EPPN
        - HTTP_SHIB_INETORGPERSON_MAIL
        - An appropriate HTTP_SHIB_EP_ENTITLEMENT
    - Optional Attributes:
        - HTTP_SHIB_INETORGPERSON_GIVENNAME
        - HTTP_SHIB_PERSON_SURNAME
* A valid domain name in peer table (passed through HTTP_SHIB_HOMEORGANIZATION)

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

Inside the static folder you will find two empty png files: logo.dist.png (172x80) and shib_login.dist.png (98x80).
Edit those two with your favourite image processing software and save them as logo.png and shib_login.png under the same folder. Image sizes are optimized to operate without any
other code changes. In case you want to incorporate images of different sizes you have to fine tune css and/or html as well.

4.2.2 Footer

Under the templates folder (templates), you can alter the footer.html file to include your own footer messages, badges, etc.

4.3 Installation

* Run:
	./manage.py syncdb
	to create all the necessary tables in the database. Enable the admin account to insert initial data for peers and their contact info.
* Then to allow for south migrations:
	./manage.py migration
* If you have properly set the primary and alternate whois servers you could go for:
	./manage.py fetch_networks
	to automatically fill network info.
	Alternatively you could fill those info manually via the admin interface.
* Via the admin interface, modify as required the existing (example.com) Site instance
* Modify flatpages to suit your needs 
* Once Apache proxying and shibboleth modules are properly setup, login to the tool. If shibboleth SP is properly setup you should see a user pending activation message and an activation email should arrive at the NOTIFY_ADMIN_MAILS accounts. 

5. UPDATING:
* from 0.9.1 to 0.9.2:
 - Check diff between urls
 - run ./manage.py migrate accounts (data migration for perms)
