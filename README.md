# Simple TOML Configurator

[![PyPI version](https://badge.fury.io/py/Simple-TOML-Configurator.svg)](https://badge.fury.io/py/Simple-TOML-Configurator)
![PyPI - License](https://img.shields.io/pypi/l/Simple-TOML-Configurator)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/Simple-TOML-Configurator)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/Simple-TOML-Configurator)
![Build](https://github.com/gilbn/Simple-TOML-Configurator/actions/workflows/tests.yml/badge.svg?event=push)

The **Simple TOML Configurator** is a versatile Python library designed to streamline the handling and organization of configuration settings across various types of applications. This library facilitates the management of configuration values through a user-friendly interface and stores these settings in TOML file format for easy readability and accessibility.

## Documentation

https://gilbn.github.io/Simple-TOML-Configurator/

## Features

1. **Effortless Configuration Management:** The heart of the library is the `Configuration` class, which simplifies the management of configuration settings. It provides intuitive methods to load, update, and store configurations, ensuring a smooth experience for developers.

2. **Universal Applicability:** The **Simple TOML Configurator** is designed to work seamlessly with any type of Python application, ranging from web frameworks like Flask, Django, and FastAPI to standalone scripts and command-line utilities.

3. **TOML File Storage:** Configuration settings are stored in TOML files, a popular human-readable format. This enables developers to review, modify, and track configuration changes easily.

4. **Attribute-Based Access:** Accessing configuration values is straightforward, thanks to the attribute-based approach. Settings can be accessed and updated as attributes, making it convenient for both reading and modifying values.

5. **Environment Variable Support:** Configuration values are automatically set as environment variables, making it easier to use the configuration values in your application. Environment variable are set as uppercase. e.g. `APP_HOST` and `APP_PORT` or `PROJECT_APP_HOST` and `PROJECT_APP_PORT` if `env_prefix` is set to "project". This also works for nested values. ex: `TABLE_KEY_LEVEL1_KEY_LEVEL2_KEY`. This works for any level of nesting.**Environment variables set before the configuration is loaded will not be overwritten, but instead will overwrite the existing config value.**

6. **Default Values:** Developers can define default values for various configuration sections and keys. The library automatically incorporates new values and manages the removal of outdated ones.

7. **Customization Capabilities:** The `Configuration` class can be extended and customized to cater to application-specific requirements. Developers can implement custom logic with getters and setters to handle unique settings or scenarios.

## Installation

Install with
```bash
pip install simple-toml-configurator
```

## Usage Example

See [Usage](https://gilbn.github.io/Simple-TOML-Configurator/latest/usage-examples/) for more examples.

```python
import os
from simple_toml_configurator import Configuration

# Define default configuration values
default_config = {
    "app": {
        "ip": "0.0.0.0",
        "host": "",
        "port": 5000,
        "upload_folder": "uploads",
    },
    "mysql": {
        "user": "root",
        "password": "root",
        "databases": {
            "prod": "db1",
            "dev": "db2",
            },
    }
}

# Set environment variables
os.environ["PROJECT_APP_UPLOAD_FOLDER"] = "overridden_uploads"

# Initialize the Simple TOML Configurator
settings = Configuration(config_path="config", defaults=default_config, config_file_name="app_config", env_prefix="project")
# Creates an `app_config.toml` file in the `config` folder at the current working directory.

# Access and update configuration values
print(settings.app.ip)  # Output: '0.0.0.0'
settings.app.ip = "1.2.3.4"
settings.update()
print(settings.app_ip)  # Output: '1.2.3.4'

# Access nested configuration values
print(settings.mysql.databases.prod)  # Output: 'db1'
settings.mysql.databases.prod = 'new_value'
settings.update()
print(settings.mysql.databases.prod)  # Output: 'new_value'

# Access and update configuration values
print(settings.app_ip)  # Output: '1.2.3.4'
settings.update_config({"app_ip": "1.1.1.1"})
print(settings.app_ip)  # Output: '1.1.1.1'

# Access all settings as a dictionary
all_settings = settings.get_settings()
print(all_settings)
# Output: {'app_ip': '1.1.1.1', 'app_host': '', 'app_port': 5000, 'app_upload_folder': 'overridden_uploads', 'mysql_user': 'root', 'mysql_password': 'root', 'mysql_databases': {'prod': 'new_value', 'dev': 'db2'}}

# Modify values directly in the config dictionary
settings.config["mysql"]["databases"]["prod"] = "db3"
settings.update()
print(settings.mysql_databases["prod"])  # Output: 'db3'

# Access environment variables
print(os.environ["PROJECT_MYSQL_DATABASES_PROD"])  # Output: 'db3'
print(os.environ["PROJECT_APP_UPLOAD_FOLDER"])  # Output: 'overridden_uploads'
```

**`app_config.toml` contents**

```toml
[app]
ip = "1.1.1.1"
host = ""
port = 5000
upload_folder = "overridden_uploads"

[mysql]
user = "root"
password = "root"

[mysql.databases]
prod = "db3"
dev = "db2"
```
