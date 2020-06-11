Shopping list
=======

GUI application with list of products. 
Made with Kivy cross-platform graphical framework and 
KivyMD - collection of Material Design compliant widgets.
Uses Redis as the DB.

>NOTE: Python3.8+ not supported

Set it up
------

1 Install Redis on your local machine by [this guide](https://redis.io/topics/quickstart)
or create your own cloud Redis service by [this guide](https://redislabs.com/redis-enterprise-cloud/).

2 Set up Redis database config. Create local.conf like this.
Section name "db" and option names "host", "port", "password" are required.

    [db]
    host: this_is_a_host_name
    port: this_is_a_port_name
    password: this_is_a_password
    
3 Get python venv module if it's not exists

    $ sudo apt-get install python3-venv
    
4 Create a virtual environment, update pip and install the requirements
>NOTE: For run Kivy on Windows see the installation guide
>[here](https://kivy.org/doc/stable/installation/installation-windows.html).
>Note that all requirements must be installed on your venv dir.

    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip install --upgrade pip
    $ pip install -r requirements.txt
    
5 Run it

    $ python .
