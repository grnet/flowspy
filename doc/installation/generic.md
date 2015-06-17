# Installing Flowspy
This guide provides general information about the installation of Flowspy. In case you use Debian Wheezy or Red Hat Linux, we provide detailed instructions for the installation.

Also it assumes that installation is carried out in `/srv/flowspy`
directory. If other directory is to be used, please change the
corresponding configuration files. It is also assumed that the `root` user
will perform every action.

## Requirements

### System Requirements
In order to install FoD properly, make sure the following software is installed on your computer.

- apache 2
- memcached
- libapache2-mod-proxy-html
- gunicorn
- beanstalkd
- mysql
- python
- pip
- libxml2-dev
- libxslt-dev
- gcc
- python-dev

### Pip
In order to install the required python packages for Flowspy you can use pip:

	pip install -r requirements.txt

### Create a database
If you are using mysql, you should create a database:

    mysql -u root -p -e 'create database fod'

### Download Flowspy
You can download Fod from GRNETs github repository. Then you have to unzip the file and place it under /srv.

	cd /tmp
	wget https://github.com/grnet/flowspy/archive/v1.2.zip
	unzip v1.2.zip
	mv flowspy-1.2 /srv/flowspy/

### Copy dist files

	cd /srv/flowspy/flowspy
	cp settings.py.dist settings.py
	cp urls.py.dist urls.py

### Device Configuration
Flowspy generates and commits flowspec rules to a
device via netconf. You have to create an account
with rw access to flowspec and set these credentials
in settings.py. See Configuration for details.


### Adding some default data
Into `/srv/flowspy` you will notice that there is a directory called `initial_data`. In there, there is a file called `fixtures_manual.xml` which contains some default static pages for django's flatpages app. In this file we have placed 4 flatpages (2 for Greek, 2 for English) with Information and Terms of Service about the service. To import the flatpages, run from `/srv/flowspy`:

	./manage.py loaddata initial_data/fixtures_manual.xml


### Beanstalkd
Just start beanstalk already!

	service beanstalkd start


### Apache2
Apache proxies gunicorn. Things are more flexible here as you may follow your own configuration and conventions.

#### Example config
Here is an example configuration.

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

