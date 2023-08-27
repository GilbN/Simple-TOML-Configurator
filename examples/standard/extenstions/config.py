
import os
from binascii import hexlify
from simple_toml_configurator import Configuration

default_config = {
    "app": {
        "ip": "0.0.0.0",
        "host": "",
        "port": 5000,
        "upload_folder": "uploads",
        "flask_secret_key": "",
        "proxy": "",
        "site_url": "http://localhost:5000",
        "debug": True,
        },
    "mysql": {
        "host": "",
        "port": "",
        "user": "",
        "password": "",
        "databases": {"prod":"test", "dev":"test2"},
        },
    "scheduler": {
        "disabled": True
        },
    "logging": {
        "debug": True
        },
    "queue": {
        "disabled": True
        },
    }

config_path = os.environ.get("CONFIG_PATH", os.path.join(os.getcwd(), "config"))
settings = Configuration()
settings.init_config(config_path, default_config)

# create random Flask secret_key if there's none in config.toml
if not settings.config.get("app", {}).get("flask_secret_key"):
    key = os.environ.get("APP_FLASK_SECRET_KEY", hexlify(os.urandom(16)).decode())
    settings.update_config({"app_flask_secret_key": key})

# Set default mysql host
if not settings.config.get("mysql",{}).get("host"):
    mysql_host = os.environ.get("MYSQL_HOST", "localhost")
    settings.update_config({"mysql_host": mysql_host})

# Set default mysql port
if not settings.config.get("mysql",{}).get("port"):
    mysql_port = os.environ.get("MYSQL_PORT", "3306")
    settings.update_config({"mysql_port": mysql_port})

# Set default mysql user
if not settings.config.get("mysql",{}).get("user"):
    mysql_user = os.environ.get("MYSQL_USER", "root")
    settings.update_config({"mysql_user": mysql_user})

# Set default mysql password
if not settings.config.get("mysql",{}).get("password"):
    mysql_password = os.environ.get("MYSQL_PASSWORD", "root")
    settings.update_config({"mysql_password": mysql_password})

if not settings.config.get("mysql",{}).get("database"):
    mysql_database = os.environ.get("MYSQL_DATABASE", "some_database")
    settings.update_config({"mysql_database": mysql_database})