from typing import Any
import os
import re
from collections.abc import Mapping
import logging
import ast
from dateutil.parser import parse, ParserError
from pathlib import Path
import tomlkit
from tomlkit import TOMLDocument
from .exceptions import *

__version__ = "1.2.1"

logger = logging.getLogger(__name__)

class Configuration:
    """Class to set our configuration values we can use around in our app.
    The configuration is stored in a toml file as well as on the instance.

    Examples:
        ```pycon
        >>> default_config = {
            "app": {
                "ip": "0.0.0.0",
                "host": "",
                "port": 5000,
                "upload_folder": "uploads"
                }
            }
        >>> import os
        >>> from simple_toml_configurator import Configuration
        >>> settings = Configuration("config", default_config, "app_config")
        {'app': {'ip': '0.0.0.0', 'host': '', 'port': 5000, 'upload_folder': 'uploads'}}
        # Update the config dict directly
        >>> settings.app.ip = "1.1.1.1"
        >>> settings.update()
        >>> settings.app.ip
        '1.1.1.1'
        >>> settings.get_settings()
        {'app_ip': '1.1.1.1', 'app_host': '', 'app_port': 5000, 'app_upload_folder': 'uploads'}
        >>> settings.update_config({"app_ip":"1.2.3.4"})
        >>> settings.app_ip
        '1.2.3.4'
        >>> settings.config.get("app").get("ip")
        '1.2.3.4'
        >>> settings.config["app"]["ip"] = "0.0.0.0"
        >>> settings.update()
        >>> settings.app_ip
        '0.0.0.0'
        >>> print(os.environ.get("APP_UPLOAD_FOLDER"))
        'uploads'
        ```

    Attributes:
        config (TOMLDocument): TOMLDocument with all config values
        config_path (str|Path): Path to config folder
        config_file_name (str): Name of the config file
        defaults (dict[str,dict]): Dictionary with all default values for your application

    !!! Info
        Changing a table name in your `defaults` will remove the old table in config including all keys and values.

    !!! Note
        If updating an attribute needs extra logic, make a custom class that inherits from this class and add property attributes with a getter and setter.

        Example:

        ```python
        from simple_toml_configurator import Configuration
        from utils import configure_logging

        class CustomConfiguration(Configuration):
            def __init__(self):
                super().__init__()

            @property
            def logging_debug(self):
                return getattr(self, "_logging_debug")

            @logging_debug.setter
            def logging_debug(self, value: bool):
                if not isinstance(value, bool):
                    raise ValueError(f"value must be of type bool not {type(value)}")
                self._logging_debug = value
                log_level = "DEBUG" if value else "INFO"
                configure_logging(log_level)
                logger.debug(f"Debug logging set to {value}")

            defaults = {
                "logging": {
                    "debug": False
                ...
                }

            config_path = os.environ.get("CONFIG_PATH", "config")
            settings = CustomConfiguration()
            settings.init_config(config_path, defaults, "app_config"))
        ```
    """

    def __init__(self, *args, **kwargs) -> None:
        self.logger = logging.getLogger("Configuration")
        if args or kwargs:
            self.init_config(*args, **kwargs)

    def __repr__(self) -> str:
        return f"Configuration(config_path={getattr(self,'config_path', None)}, defaults={getattr(self, 'defaults',None)}, config_file_name={getattr(self, 'config_file_name', None)})" # pragma: no cover
    
    def __str__(self) -> str:
        return f"<Configuration> File:'{getattr(self, 'config_file_name', None)}' Path:'{getattr(self, '_full_config_path', None)}'" # pragma: no cover

    def init_config(self, config_path:str|Path, defaults:dict[str,dict], config_file_name:str="config",env_prefix:str="") -> TOMLDocument:
        """
        Creates the config folder and toml file if needed.

        Upon init it will add any new/missing values/tables from `defaults` into the existing TOML config.
        Removes any old values/tables from `self.config` that are not in `self.defaults`.

        Sets all config keys as attributes on the class. e.g. `self.table.key`, `self.table_key` and `self._table_key`

        Env variables of all config keys are set as uppercase. e.g. `APP_HOST` and `APP_PORT` or `APP_CONFIG_APP_HOST` and `APP_CONFIG_APP_PORT` if `env_prefix` is set to "app_config".
        
        Nested tables are set as nested environment variables. e.g. `APP_CONFIG_APP_DATABASES_PROD` and `APP_CONFIG_APP_DATABASES_DEV`.

        Examples:
            ```pycon
            >>> settings = Configuration()
            >>> settings.init_config("config", defaults, "app_config"))
            ```

        Args:
            config_path (str|Path): Path to config folder
            defaults (dict[str,dict]): Dictionary with all default values for your application
            config_file_name (str, optional): Name of the config file. Defaults to "config".
            env_prefix (str, optional): Prefix for environment variables. Defaults to "".

        Returns:
            dict[str,Any]: Returns a TOMLDocument.
        """

        if not isinstance(config_path, (str, Path)):
            raise TypeError(f"argument config_path must be of type {type(str)} or {type(Path)}, not: {type(config_path)}") # pragma: no cover
        if not isinstance(defaults, dict):
            raise TypeError(f"argument defaults must be of type {type(dict)}, not: {type(defaults)}") # pragma: no cover
        if not isinstance(env_prefix, str):
            raise TypeError(f"argument env_prefix must be of type {type(str)}, not: {type(env_prefix)}") # pragma: no cover
        if not isinstance(config_file_name, str):
            raise TypeError(f"argument config_file_name must be of type {type(str)}, not: {type(config_file_name)}") # pragma: no cover

        self.defaults:dict[str,dict] = defaults
        self.config_path:str|Path = config_path
        self.config_file_name:str = f"{config_file_name}.toml"
        self.env_prefix:str = env_prefix
        self._full_config_path:str = os.path.join(self.config_path, self.config_file_name)
        self.config:TOMLDocument = self._load_config()
        self._sync_config_values()
        self._set_os_env()
        self._set_attributes()
        return self.config

    def _sync_config_values(self) -> None:
        """Add any new/missing values/tables from self.defaults into the existing TOML config
        - If a table is missing from the config, it will be added with the default table.
        - If a table is missing from the defaults, it will be removed from the config.
        If there is a mismatch in types between the default value and the config value, the config value will be replaced with the default value.
        
        For example if the default value is a string and the existing config value is a dictionary, the config value will be replaced with the default value.
        """
        def update_dict(current_dict:dict, default_dict:dict) -> dict:
            """Recursively update a dictionary with another dictionary.

            Args:
                current_dict (dict): The dictionary to update. Loaded from the config file.
                default_dict (dict): The dictionary to update with. Loaded from the defaults.

            Returns:
                dict: The updated dictionary
            """
            for key, value in default_dict.items():
                if isinstance(value, Mapping):
                    if not isinstance(current_dict.get(key, {}), Mapping):
                        logger.warning("Mismatched types for key '%s': expected dictionary, got %s. Replacing with new dictionary.", key, type(current_dict.get(key))) # pragma: no cover
                        current_dict[key] = {}
                    if key not in current_dict:
                        logger.info("Adding new Table: ('%s')", key) # pragma: no cover
                    current_dict[key] = update_dict(current_dict.get(key, {}), value)
                else:
                    if key not in current_dict:
                        logger.info("Adding new Key: ('%s':'***') in table: %s", key, current_dict) # pragma: no cover
                        current_dict[key] = value
            return current_dict

        self.config = update_dict(self.config, self.defaults)
        self._write_config_to_file()
        self._clear_old_config_values()

    def _clear_old_config_values(self) -> None:
        """Remove any old values/tables from self.config that are not in self.defaults
        """
        def remove_keys(config:dict, defaults:dict) -> None:
            # Create a copy of config to iterate over
            config_copy = config.copy()

            # Remove keys that are in config but not in defaults
            for key in config_copy:
                if key not in defaults:
                    del config[key]
                    logger.info("Removing Key: ('%s') in Table: ( '%s' )", key, config_copy)
                elif isinstance(config[key], Mapping):
                    remove_keys(config[key], defaults[key])

        remove_keys(self.config, self.defaults)
        self._write_config_to_file()

    def get_settings(self) -> dict[str, Any]:
        """Get all config key values as a dictionary.
        
        Dict keys are formatted as: `table_key`:
        
        Examples:
            ```pycon
            >>> defaults = {...}
            >>> settings = Configuration()
            >>> settings.init_config("config", defaults, "app_config"))
            >>> settings.get_settings()
            {'app_ip': '0.0.0.0', 'app_host': '', 'app_port': 5000, 'app_upload_folder': 'uploads'}
            ```

        Returns:
            dict[str, Any]: Dictionary with config key values.
        """
        settings: dict[str, Any] = {}
        for table in self.config:
            for key, value in self.config[table].items():
                settings[f"{table}_{key}"] = value
        return settings

    def _set_attributes(self) -> dict[str, Any]:
        """Set all config keys as attributes on the class.

        Two different attributes are set for each key.
        _TOMLtable_key: e.g. `_app_host`
        TOMLtable_key: e.g. `app_host`
        
        This makes it so that the instance attributes are updated when the a value in self.config is updated as they reference the same object.

        Returns:
            dict[str, Any]: Returns all attributes in a dictionary
        """
        for table in self.config:
            setattr(self,table,ConfigObject(self.config[table]))
            for key, value in self.config[table].items():
                setattr(self, f"_{table}_{key}", value)
                setattr(self, f"{table}_{key}", value)
                self._update_os_env(table, key, value)

    def _parse_env_value(self, value:str) -> Any:
        """Parse the environment variable value to the correct type.
        
        Args:
            value (str): The value to parse
        
        Returns:
            Any: The parsed value as the correct type or the original value if it could not be parsed.
        """
        if str(value).lower() == "true":
            return True
        if str(value).lower() == "false":
            return False
        try:
            parsed_value = ast.literal_eval(value)
            if isinstance(parsed_value, (int, float, bool, str, list, dict)):
                return parsed_value
        except (ValueError, SyntaxError):
            pass
        try:
            return parse(value)
        except ParserError:
            pass
        return str(value)

    def _make_env_name(self, table:str, key:str) -> str:
        """Create an environment variable name from the table and key.

        Args:
            table (str): The table name
            key (str): The key name
            
        Returns:
            str: The environment variable name
        """
        if self.env_prefix:
            return f"{self.env_prefix.upper()}_{table.upper()}_{str(key).upper()}"
        return f"{table.upper()}_{str(key).upper()}"

    def _update_os_env(self, table:str, key:str, value:Any) -> None:
        """Update the os environment variable with the same name as the config table and key.

        If the value is a dictionary, creates an environment variable for each item in the dictionary,
        handling nested dictionaries recursively.

        Args:
            table (str): The table name
            key (str): The key name
            value (Any): The value
        """
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                self._update_os_env(table, f"{key}_{subkey}", subvalue)
        else:
            env_var = self._make_env_name(table, key)
            os.environ[env_var] = str(value)

    def _set_os_env(self) -> None:
        """Set all config keys as environment variables.

        The environment variable is set as uppercase. e.g. `APP_HOST` and `APP_PORT` or `APP_CONFIG_APP_HOST` and `APP_CONFIG_APP_PORT` if `env_prefix` is set to "app_config".
        
        If the environment variable already exists, the config value is updated to the env value and will overwrite any config value.
        """
        for table in self.config.copy():
            for key, value in self.config[table].items():
                existing_env = os.environ.get(self._make_env_name(table, key))
                if existing_env:
                    logger.info("Setting Table: ('%s') Key: ('%s') to value from existing environment variable: ('%s')",table, key, existing_env)
                    self.config[table][key] = self._parse_env_value(existing_env)
                    continue
                self._update_os_env(table, key, value)
        self._write_config_to_file()

    def update_config(self, settings: dict[str,Any]) -> None:
        """Update all config values from a dictionary, set new attribute values and write the config to file.
        Use the same format as `self.get_settings()` returns to update the config.

        Examples:
        ```pycon
        >>> defaults = {"mysql": {"databases": {"prod":"prod_db1", "dev":"dev_db1"}}}
        >>> settings = Configuration()
        >>> settings.init_config("config", defaults, "app_config")
        >>> settings.update_config({"mysql_databases": {"prod":"prod_db1", "dev":"dev_db2"}})
        print(settings.mysql_databases["dev"])
        'dev_db2'
        ```

        Args:
            settings (dict): Dict with key values
        """
        if not isinstance(settings, dict):
            raise TypeError(f"Argument settings must be of type {type(dict)}, not: {type(settings)}") # pragma: no cover
        try:
            for table in self.config:
                for key, value in settings.items():
                    table_key = key.split(f"{table}_")[-1]
                    if self.config.get(table) and table_key in self.config[table].keys():
                        if self.config[table][table_key] != value:
                            self.logger.info("Updating TOML Document -> Table: ('%s') Key: ('%s')",table, table_key)
                            self.config[table][table_key] = value
        except Exception as exc: # pragma: no cover
            self.logger.exception("Could not update config!")
            raise TOMLConfigUpdateError("unable to update config!") from exc
        self._write_config_to_file()
        self._set_attributes()
    
    def update(self):
        """Write the current config to file.

        Examples:
        ```pycon
        >>> from simple_toml_configurator import Configuration
        >>> settings = Configuration()
        >>> defaults = {"mysql": {"databases": {"prod":"prod_db1", "dev":"dev_db1"}}}
        >>> settings.init_config("config", defaults, "app_config")
        >>> settings.mysql.databases.prod = "prod_db2"
        >>> settings.update()
        >>> settings.config["mysql"]["databases"]["prod"]
        'prod_db2'
        >>> settings.config["mysql"]["databases"]["prod"] = "prod_db3"
        >>> settings.update()
        >>> settings.mysql_databases["prod"]
        'prod_db3'
        ```
        """
        self._write_config_to_file()
        self._set_attributes()

    def _write_config_to_file(self) -> None:
        """Update and write the config to file"""
        self.logger.debug("Writing config to file")
        try:
            with Path(self._full_config_path).open("w") as conf:
                toml_document = tomlkit.dumps(self.config)
                # Use regular expression to replace consecutive empty lines with a single newline
                cleaned_toml = re.sub(r'\n{3,}', '\n\n', toml_document)
                conf.write(cleaned_toml)
        except (OSError,FileNotFoundError,TypeError) as exc: # pragma: no cover
            self.logger.exception("Could not write config file!")
            raise TOMLWriteConfigError("unable to write config file!") from exc # pragma: no cover
        self.config = self._load_config()

    def _load_config(self) -> TOMLDocument:
        """Load the config from file and return it as a TOMLDocument"""
        try:
            return tomlkit.loads(Path(self._full_config_path).read_text())
        except FileNotFoundError: # pragma: no cover
            self._create_config(self._full_config_path) # Create the config folder and toml file if needed.
            try:
                return tomlkit.loads(Path(self._full_config_path).read_text())
            except Exception as exc:
                self.logger.exception("Could not load config file!")
                raise TOMLLoadConfigError("unable to load config file!") from exc

    def _create_config(self, config_file_path:str) -> None:
        """Create the config folder and toml file.

        Args:
            config_file_path (str): Path to the config file
        """
        
        # Check if config path exists
        try:
            if not os.path.isdir(os.path.dirname(config_file_path)):
                os.makedirs(os.path.dirname(config_file_path), exist_ok=True) # pragma: no cover
        except OSError as exc: # pragma: no cover
            self.logger.exception("Could not create config folder!")
            raise  TOMLCreateConfigError(f"unable to create config folder: ({os.path.dirname(config_file_path)})") from exc # pragma: no cover
        try:
            self.logger.debug("Creating config")
            with Path(config_file_path).open("w") as conf:
                conf.write(tomlkit.dumps(self.defaults))
        except OSError as exc: # pragma: no cover
            self.logger.exception("Could not create config file!")
            raise TOMLCreateConfigError(f"unable to create config file: ({config_file_path})") from exc

class ConfigObject:
    """
    Represents a configuration object that wraps a dictionary and provides attribute access.

    Any key in the dictionary can be accessed as an attribute.
    
    Args:
        table (dict): The dictionary representing the configuration.

    Attributes:
        _table (dict): The internal dictionary representing the configuration.

    """

    def __init__(self, table: dict):
        self._table = table
        for key, value in table.items():
            if isinstance(value, dict):
                self.__dict__[key] = ConfigObject(value)
            else:
                self.__dict__[key] = value

    def __setattr__(self, __name: str, __value: Any) -> None:
        """Update the table value when an attribute is set"""
        super().__setattr__(__name, __value)
        if __name == "_table":
            return
        if hasattr(self, "_table") and __name in self._table:
            self._table[__name] = __value

    def __repr__(self) -> str:
        return f"ConfigObject({self._table})"

    def __str__(self) -> str:
        return f"<ConfigObject> {self._table}"