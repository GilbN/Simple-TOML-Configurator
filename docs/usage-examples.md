## Usage Examples

### Initializing Configuration

To get started with the Simple TOML Configurator, you need to initialize the configuration settings using the `init_config` method or init `Configuration` object with the arguments. This sets up the default values and configuration file paths.

```python
from simple_toml_configurator import Configuration

# Define default configuration values
default_config = {
    "app": {
        "ip": "0.0.0.0",
        "host": "",
        "port": 5000,
        "upload_folder": "uploads"
    },
    "mysql": {
        "databases": {
            "prod": "db1",
            "dev": "db2"
        }
    }
}

# Initialize the Simple TOML Configurator
settings = Configuration()
settings.init_config("config", default_config, "app_config")
```

#### Load defaults from a TOML file

```python
from simple_toml_configurator import Configuration
import tomlkit
import os
from pathlib import Path

default_file_path = Path(os.path.join(os.getcwd(), "default.toml"))
defaults = tomlkit.loads(file_path.read_text())
settings = Configuration("config", defaults, "app_config")
```

### Accessing Configuration Values

You can access configuration values as attributes of the `Configuration` instance. This attribute-based access makes it straightforward to retrieve settings.
There are two main ways to access configuration values:

1. Attribute access:
    - This is the default access method. ex: `settings.app.ip`

2. Table prefix access:
    - Add the table name as a prefix to the key name. ex: `settings.app_ip` instead of `settings.app.ip`. **This only works for the first level of nesting.**

!!! info Attribute access
    If the table contains a nested table, you can access the nested table using the same syntax. ex: `settings.mysql.databases.prod`

    !!! note
        This works for any level of nesting.

### Environment variable access

Access the configuration values as environment variables. ex: `APP_IP` instead of `settings.app.ip`.

Or `APP_CONFIG_APP_IP` if `env_prefix` is set to "app_config".

You can also access nested values. ex: `MYSQL_DATABASES_PROD`.

!!! note
    This works for any level of nesting.

### Updating Configuration Settings

Use the `update_config` or `update` method to modify values while ensuring consistency across instances.

#### update() method

```python
# Update the ip key in the app table
settings.app.ip = "1.2.3.4"
settings.update()
```

#### update_config() method

```python
# Update the ip key in the app table
settings.update_config({"app_ip": "1.2.3.4"})
```

#### Update the config dictionary directly

You can directly modify configuration values within the `config` dictionary. After making changes, use the `update` method to write the updated configuration to the file.

```python
# Modify values directly and update configuration
settings.config["app"]["ip"] = "0.0.0.0"
settings.update()
```

### Accessing All Settings

Retrieve all configuration settings as a dictionary using the `get_settings` method. This provides an overview of all configured values.

```python
# Get all configuration settings
all_settings = settings.get_settings()
print(all_settings) # Output: {'app_ip': '1.2.3.4', 'app_host': '', 'app_port': 5000, 'app_upload_folder': 'uploads'}
```

### Customization with Inheritance

For advanced use cases, you can create a custom configuration class by inheriting from `Configuration`. This allows you to add custom logic and properties tailored to your application.

```python
from simple_toml_configurator import Configuration

class CustomConfiguration(Configuration):
    def __init__(self):
        super().__init__()

    # Add custom properties with getters and setters
    @property
    def custom_setting(self):
        return getattr(self, "_custom_setting")

    @custom_setting.setter
    def custom_setting(self, value):
        # Custom logic for updating custom_setting
        self._custom_setting = value
        # Additional actions can be performed here

# Initialize and use the custom configuration
custom_settings = CustomConfiguration()
custom_settings.init_config("config", default_config, "custom_config")
```