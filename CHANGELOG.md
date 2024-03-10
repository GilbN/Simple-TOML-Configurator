# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog],
and this project adheres to [Semantic Versioning].

## [Unreleased]

- /

## [1.2.2] - 2024-03-10

## New Release v.1.2.2

## Fixes

Fixes `TypeError: unsupported operand type(s) for |: 'type' and 'type'.` error when using Python version < 3.10

## [1.2.1] - 2024-02-04

## New Release: v1.2.1 - Set environment variables from configuration.

### What's New

Environment variable are now automatically set from the configuration. This makes it easier to use the configuration values in your application.
Env variables of all config keys are set as uppercase. e.g. `APP_HOST` and `APP_PORT` or `APP_CONFIG_APP_HOST` and `APP_CONFIG_APP_PORT` if `env_prefix` is set to "app_config".

It will also try and convert the values to the correct type. e.g. `APP_PORT` will be set as an integer if the env value is `8080`

Nested values can also be accessed. ex: `TABLE_KEY_LEVEL1_KEY_LEVEL2_KEY`. This works for any level of nesting.

Any existing env variables that matches will not be overwritten, but instead will overwrite the existing config value.

```python
import os
from simple_toml_configurator import Configuration

os.environ["PROJECT_APP_PORT"] = "1111"
default = {"app": {"host": "localhost", "port": 8080}}
config = Configuration(
    config_path="config_folder",
    defaults=default,
    config_file_name="app_settings",
    env_prefix="project")

print(os.environ["PROJECT_APP_HOST"])  # Output: 'localhost'
print(os.environ["PROJECT_APP_PORT"])  # Output: '1111'
```

### Fixes

- Fixed a bug where update_config() would not update the attributes of the Configuration object.

## [1.1.0] - 2024-01-28

## New Release: v1.1.0 - True Nested Configuration Support with Attribute Access

This release introduces a significant new feature: Nested Configuration Support with Attribute Access.

### What's New

**Nested Configuration Support with Attribute Access:** In previous versions, accessing and updating nested configuration values required dictionary-style access. With this release, we've made it easier and more intuitive to work with nested configuration values. Now, you can access and update these values using attribute-style access, similar to how you would interact with properties of an object in JavaScript.

Here's an example:

```python
# Access nested configuration values
print(settings.mysql.databases.prod)  # Output: 'db1'
settings.mysql.databases.prod = 'new_value'
settings.update()
print(settings.mysql.databases.prod)  # Output: 'new_value'
```

## [1.0.0] - 2023-08-27

- initial release

<!-- Links -->
[keep a changelog]: https://keepachangelog.com/en/1.0.0/
[semantic versioning]: https://semver.org/spec/v2.0.0.html

<!-- Versions -->
[unreleased]: https://github.com/gilbn/simple-toml-configurator/compare/1.2.2...HEAD
[1.2.2]: https://github.com/gilbn/simple-toml-configurator/releases/tag/1.2.2
[1.2.1]: https://github.com/gilbn/simple-toml-configurator/releases/tag/1.2.1
[1.1.0]: https://github.com/gilbn/simple-toml-configurator/releases/tag/1.1.0
[1.0.0]: https://github.com/gilbn/simple-toml-configurator/releases/tag/1.0.0