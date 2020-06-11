import os
import sys
from configparser import ConfigParser, NoSectionError, NoOptionError

import redis

from app import App


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

local_config_path = os.path.join(BASE_DIR, 'local.conf')
config = ConfigParser()
config.read(local_config_path)

if not os.path.isfile(local_config_path):
    print(
        'ERROR: Can\'t find config file for connection to server. '
        'Config file named "local.conf" expected.',
        file=sys.stderr
    )
    sys.exit(1)

try:
    HOST = config.get('db', 'host')
    PORT = config.get('db', 'port')
    PASSWORD = config.get('db', 'password')

except NoSectionError:
    print(
        'ERROR: Wrong section name in local.conf. '
        'Section named "db" expected.',
        file=sys.stderr
    )
    sys.exit(1)

except NoOptionError:
    print(
        'ERROR: Wrong option name in local.conf. '
        'Valid option names: "host", "port", "password".',
        file=sys.stderr
    )
    sys.exit(1)

if not all((HOST, PORT, PASSWORD)):
    print(
        'ERROR: Can\'t find config in local.conf. Valid section name: "db", '
        'valid option names: "host", "port", "password".',
        file=sys.stderr
    )
    sys.exit(1)


db = redis.Redis(host=HOST, port=PORT, password=PASSWORD)
App(db).run()
