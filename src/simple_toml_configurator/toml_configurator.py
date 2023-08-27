from typing import Any
import os
import tomlkit
from tomlkit import TOMLDocument
from pathlib import Path
import logging

from .exceptions import *

__version__ = "1.0.0"

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
        >>> from simple_toml_configurator import Configuration
        >>> settings = Configuration("config", default_config, "app_config")
        {'app': {'ip': '0.0.0.0', 'host': '', 'port': 5000, 'upload_folder': 'uploads'}}
        >>> settings.get_settings()
        {'app_ip': '0.0.0.0', 'app_host': '', 'app_port': 5000, 'app_upload_folder': 'uploads'}
        >>> settings.update_config({"app_ip":"1.2.3.4"})
        >>> settings.app_ip
        '1.2.3.4'
        >>> settings.config.get("app").get("ip")
        '1.2.3.4'
        # Update the config dict directly
        >>> settings.config["app"]["ip"] = "0.0.0.0"
        >>> settings.update()
        >>> settings.app_ip
        '0.0.0.0'
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

    def init_config(self, config_path:str|Path, defaults:dict[str,dict], config_file_name:str="config") -> TOMLDocument:
        """
        Creates the config folder and toml file if needed.

        Upon init it will add any new/missing values/tables from `defaults` into the existing TOML config.
        Removes any old values/tables from `self.config` that are not in `self.defaults`.

        Sets all config keys as attributes on the class. e.g. `self.table_key` and `self._table_key =`

        Examples:
            ```pycon
            >>> settings = Configuration()
            >>> settings.init_config("config", defaults, "app_config"))
            ```

        Args:
            config_path (str|Path): Path to config folder
            defaults (dict[str,dict]): Dictionary with all default values for your application
            config_file_name (str, optional): Name of the config file. Defaults to "config".

        Returns:
            dict[str,Any]: Returns a TOMLDocument.
        """

        if not isinstance(config_path, (str, Path)):
            raise TypeError(f"argument config_path must be of type {type(str)} or {type(Path)}, not: {type(config_path)}") # pragma: no cover
        if not isinstance(defaults, dict):
            raise TypeError(f"argument defaults must be of type {type(dict)}, not: {type(defaults)}") # pragma: no cover

        self.defaults:dict[str,dict] = defaults
        self.config_path:str|Path = config_path
        self.config_file_name:str = f"{config_file_name}.toml"
        self._full_config_path:str = os.path.join(self.config_path, self.config_file_name)
        self.config:TOMLDocument = self._load_config()
        self._sync_config_values()
        self._set_attributes()
        return self.config

    def _sync_config_values(self) -> None:
        """Add any new/missing values/tables from self.defaults into the existing TOML config"""
        for default_table in self.defaults:
            if default_table not in self.config.keys():
                self.logger.info("Adding new TOML table: ('%s') to TOML Document", default_table)
                self.config[default_table] = self.defaults[default_table]
                continue
            if default_table in self.config.keys():
                for default_key, default_value in self.defaults[default_table].items():
                    if default_key not in self.config[default_table].keys():
                        self.logger.info("Adding new Key: ('%s':'***') to Table: ('%s')", default_key, default_table) # pragma: no cover
                        self.config[default_table][default_key] = default_value # pragma: no cover
        self._write_config_to_file()
        self._clear_old_config_values()

    def _clear_old_config_values(self) -> None:
        """Remove any old values/tables from self.config that are not in self.defaults
        """
        for table in self.config:
            if table not in self.defaults.keys():
                self.config.remove(table) # pragma: no cover
                self._write_config_to_file() # pragma: no cover
                return self._clear_old_config_values() # pragma: no cover
            for key in list(self.config[table].keys()):
                if key not in self.defaults[table]:
                    self.config[table].remove(key)
                    self._write_config_to_file()
                    continue

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
            for key, value in self.config[table].items():
                setattr(self, f"_{table}_{key}", value)
                setattr(self, f"{table}_{key}", value)

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
    
    def update(self):
        """Write the current config to file.

        Examples:
        ```pycon
        >>> from simple_toml_configurator import Configuration
        >>> settings = Configuration()
        >>> defaults = {"mysql": {"databases": {"prod":"prod_db1", "dev":"dev_db1"}}}
        >>> settings.init_config("config", defaults, "app_config")
        >>> settings.mysql_databases["prod"]
        'prod_db1'
        >>> settings.config["mysql"]["databases"]["prod"] = "prod_db2"
        >>> settings.update()
        >>> {settings.mysql_databases["prod"]}
        'prod_db2'
        ```
        
        Args:
            settings (dict): Dict with key values
        """
        self._write_config_to_file()
        self._set_attributes()

    def _write_config_to_file(self) -> None:
        """Update and write the config to file"""
        self.logger.debug("Writing config to file")
        try:
            with Path(self._full_config_path).open("w") as conf:
                conf.write(tomlkit.dumps(self.config))
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