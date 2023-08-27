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
    }
}

# Initialize the Simple TOML Configurator
settings = Configuration()
settings.init_config("config", default_config, "app_config")
```

### Accessing Configuration Values

You can access configuration values as attributes of the `settings` instance. This attribute-based access makes it straightforward to retrieve settings.

```python
# Access configuration values
ip_address = settings.app_ip
port_number = settings.app_port
upload_folder = settings.app_upload_folder
```

### Updating Configuration Settings

Updating configuration settings is seamless with the Simple TOML Configurator. Use the `update_config` method to modify values while ensuring consistency across instances.

```python
# Update a configuration value
settings.update_config({"app_ip": "1.2.3.4"})
```

### Accessing All Settings

Retrieve all configuration settings as a dictionary using the `get_settings` method. This provides an overview of all configured values.

```python
# Get all configuration settings
all_settings = settings.get_settings()
```

### Direct Configuration Modification

You can directly modify configuration values within the `config` dictionary. After making changes, use the `update` method to write the updated configuration to the file.

```python
# Modify values directly and update configuration
settings.config["app"]["ip"] = "0.0.0.0"
settings.update()
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