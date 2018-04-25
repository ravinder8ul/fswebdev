# Linux Server Configuration Project

Following is the Lightsail Server details:

- IP address: 

- Accesible SSH port: 2200

- Application URL: http://18.188.133.213/catalog/

## Walkthrough

1. Create an Amazon Lighsail server as per the instructions in the lecture notes

2. From the Lightsail page for your instance, go to the Networking tab and find the 'Add another' at the bottom. Add port 123 and 2200

3. Download the default private key from your Lightsail Account page.

4. Move your downloaded .pem public key file into .ssh folder (under home directory) of your local linux machine

5. To make the public key usable and secure, in the input terminal, `chmod 600 ~/.ssh/YourAWSKey.pem`

6. We now use this key to log into our Amazon Lightsail Server: `$ ssh -i ~/.ssh/YourAWSKey.pem ubuntu@18.188.133.213`

7. Create new user named grader and give it the permission to sudo
  - SSH into the server through `ssh -i ~/.ssh/udacity_key.rsa root@35.167.27.204`
  - Run `$ sudo adduser grader` to create a new user named grader
  - Create a new file in the sudoers directory with `sudo nano /etc/sudoers.d/grader`
  - Add the following text `grader ALL=(ALL:ALL) ALL`
  - Run `sudo nano /etc/hosts` 
  - Prevent the error `sudo: unable to resolve host` by adding this line `127.0.1.1 ip-172-26-9-104`

8. Update all currently installed packages
- `$ sudo apt-get update`
- `$ sudo apt-get upgrade`
- `$ sudo apt-get install finger`

9. Change SSH port from 22 to 2200
  - Run `sudo nano /etc/ssh/sshd_config`
  - Change the port from 22 to 2200
  - Confirm by running `ssh -i ~/.ssh/YourAWSKey.pem ubuntu@18.188.133.213 -p 2200`

10. Configure the Uncomplicated Firewall (UFW) to only allow incoming connections for SSH (port 2200), HTTP (port 80), and NTP (port 123)
  - `sudo ufw allow 2200/tcp`
  - `sudo ufw allow 80/tcp`
  - `sudo ufw allow 123/udp`
  - `sudo ufw enable`

11. Configure the local timezone to UTC
  - Run `sudo dpkg-reconfigure tzdata` and then choose UTC

12. Open a new Terminal window (Command+N) on your local machine and input `$ ssh-keygen -f ~/.ssh/grader`

13. On the Lightsail terminal window
  - `sudo su grader`
  - Create a .ssh directory: `$ mkdir .ssh`
  - `$ vi .ssh/authorized_keys`
  - Copy the contents of grader.pub file on your local machine to authorized_keys file
  - Change the permission: `$ sudo chmod 700 /home/grader/.ssh` and `$ sudo chmod 644 /home/grader/.ssh/authorized_keys`

14. Restart the ssh service: `$ sudo service ssh restart`

15. Type `$ ~.` to disconnect from Amazon Lightsail

16. Log into the server as grader: `$ ssh grader@18.188.133.213 -i .ssh/grader -p 2200`

17. Enforce key-based authentication:
  - `$ sudo vi /etc/ssh/sshd_config`
  - Find the *PasswordAuthentication* line and change text after to `no`
  - Restart ssh again: `$ sudo service ssh restart`

18. Disable ssh login for *root* user:
  - `$ sudo vi /etc/ssh/sshd_config`
  - Find the *PermitRootLogin* line and edit to `no`
  - Restart ssh `$ sudo service ssh restart`

## Deploy Catalog Application

Login to the Amazon Lightsail through Terminal with grader user as mentione above

1. Install required packages
  - `$ sudo apt-get install apache2`
  - `$ sudo apt-get install libapache2-mod-wsgi python-dev`
  - `$ sudo apt-get install git`

2. Enable mod_wsgi by `$ sudo a2enmod wsgi` and start the web server by `$ sudo service apache2 start` or `$ sudo service apache2 restart`.

3. Set up the folder structure:
  - `$ cd /var/www`
  - `$ sudo mkdir catalog`
  - `$ sudo chown -R grader:grader catalog`
  - `$ cd catalog`

4. Now clone the project from Github: `$ git clone [your link] catalog`

5. Inside folder /var/www/catalog create a catalog.wsgi file and add the following into this file:
```
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/catalog/")

from catalog import app as application
application.secret_key = 'supersecretkey'
``` 

6. Change folder to /var/www/catalog/catalog and rename `application.py` to `__init__.py`

7. Install and start the virtual machine:
  - `$ sudo pip install virtualenv`
  - `$ sudo virtualenv venv`
  - `$ source venv/bin/activate`
  - `$ sudo chmod -R 777 venv`

8. While in virtual environment install Flask and few other packages:
  - `$ sudo apt-get install python-pip`
  - `$ pip install Flask`
  - `$ pip install httplib2`
  - `$ pip install requests`
  - `$ pip install psycopg2`
  - `$ pip install httplib2`
  - `$ pip install oauth2client`
  - `$ pip install sqlalchemy`
  - `$ pip install sqlaclemy_utils`
  - `$ pip install redirect`
  - `$ pip install render_template`
  
9. In the __init__.py file, change the `client_secrets.json` line to `/var/www/catalog/catalog/client_secrets.json`

10. Now configure and enable the virtual host:
  - `$ sudo vi /etc/apache2/sites-available/catalog.conf`
  - Paste the following code and save
```
<VirtualHost *:80>
    ServerName [YOUR PUBLIC IP ADDRESS]
    ServerAlias [YOUR AMAZON LIGHTSAIL HOST NAME]
    ServerAdmin admin@35.167.27.204
    WSGIDaemonProcess catalog python-path=/var/www/catalog:/var/www/catalog/venv/lib/python2.7/site-packages
    WSGIProcessGroup catalog
    WSGIScriptAlias / /var/www/catalog/catalog.wsgi
    <Directory /var/www/catalog/catalog/>
        Order allow,deny
        Allow from all
    </Directory>
    Alias /static /var/www/catalog/catalog/static
    <Directory /var/www/catalog/catalog/static/>
        Order allow,deny
        Allow from all
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/error.log
    LogLevel warn
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```
11. Set up the database using:
  - `$ sudo apt-get install libpq-dev python-dev`
  - `$ sudo apt-get install postgresql postgresql-contrib`
  - `$ sudo su - postgres -i`

12. In postgres create a database named `catalog` with user `catalog`

13. Inside __init__.py and the database setup script, change all the `engine` references to `engine = create_engine('postgresql://catalog:[your password]@localhost/catalog`

14. Initialize the database with the database script

15. Restart Apache server `$ sudo service apache2 restart` and enter your public IP address

## Most important packages to build this app:
  - apache2
  - libapache2-mod-wsgi
  - postgresql postgresql-contrib
  - python-psycopg2 python-flask
  - oauth2client
  - requests
  - httplib2
  - render_template

## Reference
I am thankful to the following step-by-step approach:
https://github.com/callforsky/udacity-linux-configuration

