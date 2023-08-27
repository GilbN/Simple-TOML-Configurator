# Simple TOML Configurator

The **Simple TOML Configurator** is a versatile Python library designed to streamline the handling and organization of configuration settings across various types of applications. This library facilitates the management of configuration values through a user-friendly interface and stores these settings in TOML file format for easy readability and accessibility.

## Features

1. **Effortless Configuration Management:** The heart of the library is the `Configuration` class, which simplifies the management of configuration settings. It provides intuitive methods to load, update, and store configurations, ensuring a smooth experience for developers.

2. **Universal Applicability:** The **Simple TOML Configurator** is designed to work seamlessly with any type of Python application, ranging from web frameworks like Flask, Django, and FastAPI to standalone scripts and command-line utilities.

3. **TOML File Storage:** Configuration settings are stored in TOML files, a popular human-readable format. This enables developers to review, modify, and track configuration changes easily.

4. **Attribute-Based Access:** Accessing configuration values is straightforward, thanks to the attribute-based approach. Settings can be accessed and updated as attributes, making it convenient for both reading and modifying values.

5. **Updating Configurations:** The library enables the updating of configuration settings from a dictionary, ensuring that the changes are accurately reflected both in-memory and in the stored TOML file.

6. **Default Values:** Developers can define default values for various configuration sections and keys. The library automatically incorporates new values and manages the removal of outdated ones.

7. **Customization Capabilities:** The `Configuration` class can be extended and customized to cater to application-specific requirements. Developers can implement custom logic with getters and setters to handle unique settings or scenarios.

## Usage Example

```python
from simple_toml_configurator import Configuration

# Define default configuration values
default_config = {
    "app": {
        "ip": "0.0.0.0",
        "host": "",
        "port": 5000,
        "upload_folder": "uploads"
    }
    "mysql": {
        "user": "root",
        "password": "root"
        "databases": {
            "prod": "db1",
            "dev": "db2"
            }
    }
}

# Initialize the Simple TOML Configurator
settings = Configuration()
settings.init_config("config", default_config, "app_config")
# Stores an app_config.toml file in the `config` folder at the current working directory.

# Access and update configuration values
print(settings.app_ip)  # Output: '0.0.0.0'
settings.update_config({"app_ip": "1.2.3.4"})
print(settings.app_ip)  # Output: '1.2.3.4'

# Access all settings as a dictionary
all_settings = settings.get_settings()
print(all_settings)
# Output: {'app_ip': '1.2.3.4', 'app_host': '', 'app_port': 5000, 'app_upload_folder': 'uploads'}

# Modify values directly in the config dictionary
settings.config["mysql"]["databases"]["prod"] = "db3"
settings.update()
print(settings.mysql_databases["prod"])  # Output: 'db3'
```

The **Simple TOML Configurator** empowers developers to efficiently manage configuration settings across a wide range of Python applications. Whether you're building a web application, a command-line tool, or a standalone script, this library provides the tools you need to maintain and access configuration values with ease and clarity.