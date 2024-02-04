import os
from datetime import datetime
import pytest
from pathlib import Path
from tomlkit import TOMLDocument
from simple_toml_configurator import Configuration
from simple_toml_configurator.toml_configurator import ConfigObject

@pytest.fixture
def tmp_config_file_name() -> str:
    yield "config"

@pytest.fixture
def tmp_config_path(tmp_path) -> str:
    yield tmp_path

@pytest.fixture
def default_config() -> dict[str, dict]:
    yield {
        "logging": {
            "debug": False
        }
    }

@pytest.fixture
def config_instance(tmp_config_path,default_config,tmp_config_file_name) -> Configuration:
    config = Configuration()
    config.init_config(tmp_config_path, default_config, tmp_config_file_name)
    yield config

@pytest.fixture
def config_instance_env_prefix(tmp_config_path,default_config,tmp_config_file_name) -> Configuration:
    config = Configuration()
    config.init_config(tmp_config_path, default_config, tmp_config_file_name,env_prefix="TEST")
    yield config

def test_init_config(config_instance: Configuration, tmp_config_path: str, tmp_config_file_name: str, default_config: dict[str, dict]):

    assert isinstance(tmp_config_path, (str, Path))
    assert isinstance(tmp_config_file_name, str)
    assert isinstance(default_config, dict)

    config_instance.init_config(tmp_config_path, default_config, tmp_config_file_name)
    assert isinstance(config_instance.config, TOMLDocument)
    assert config_instance.config_path == tmp_config_path
    assert config_instance.defaults == default_config
    assert config_instance.config_file_name == f"{tmp_config_file_name}.toml"

def test_sync_config_values(config_instance: Configuration):
    config_instance.defaults = {
        "logging": {
            "debug": False,
            "level": "info"
        }
    }
    config_instance.config = TOMLDocument()
    config_instance._sync_config_values()
    assert "logging" in config_instance.config
    assert "debug" in config_instance.config["logging"]
    assert "level" in config_instance.config["logging"]
    assert config_instance.config["logging"]["level"] == "info"

def test_clear_old_config_values(config_instance: Configuration):
    config_instance.defaults = {
        "logging": {
            "debug": False
        }
    }
    config_instance.config = TOMLDocument()
    config_instance.config["logging"] = {
        "debug": False,
        "level": "info"
    }
    config_instance._clear_old_config_values()
    assert "level" not in config_instance.config["logging"]

def test_get_settings(config_instance: Configuration):
    config_instance.config = TOMLDocument()
    config_instance.config["app"] = {
        "host": "localhost",
        "port": 8080
    }
    settings = config_instance.get_settings()
    assert settings == {"app_host": "localhost", "app_port": 8080}

def test_set_attributes(config_instance: Configuration):
    config_instance.config = TOMLDocument()
    config_instance.config["app"] = {
        "host": "localhost",
        "port": 8080
    }
    config_instance._set_attributes()
    assert hasattr(config_instance, "_app_host")
    assert hasattr(config_instance, "app_host")
    assert config_instance._app_host == "localhost"
    assert config_instance.app_host == "localhost"
    assert config_instance.app.host == "localhost"

def test_update_config(config_instance: Configuration):
    config_instance.config = TOMLDocument()
    config_instance.config["app"] = {
        "host": "localhost",
        "port": 8080
    }
    config_instance.update_config({"app_host": "test_localhost", "app_port": 8888})
    assert config_instance.config["app"]["host"] == "test_localhost"
    assert config_instance.config["app"]["port"] == 8888
    assert config_instance.app_host == "test_localhost"
    assert config_instance.app.port == 8888

def test_write_config_to_file(config_instance: Configuration, default_config: dict[str, dict]):
    config_instance.config = TOMLDocument()
    config_instance.config = default_config
    config_instance._write_config_to_file()
    assert config_instance.config == default_config

def test_load_config(config_instance: Configuration):
    config_instance.config = TOMLDocument()
    config_instance.config["app"] = {
        "host": "localhost",
        "port": 8080
    }
    config_instance._write_config_to_file()
    assert config_instance._load_config() == config_instance.config

def test_create_config(config_instance: Configuration):
    config_instance.config = TOMLDocument()
    config_instance.defaults = {
        "app": {
            "host": "local",
            "port": 1000
    }}
    config_instance._create_config(config_instance._full_config_path)
    assert os.path.exists(config_instance._full_config_path)
    assert config_instance._load_config() == config_instance.defaults

def test_update(config_instance: Configuration, default_config: dict[str, dict]):
    config_instance.config = default_config
    config_instance.config["logging"]["debug"] = True
    config_instance.update()
    assert config_instance.logging_debug is True

def test_update_attribute(config_instance: Configuration):
    config_instance.logging.debug = True
    config_instance.update()
    assert config_instance.logging_debug is True
    assert config_instance.config["logging"]["debug"] is True

def test_os_environment_variables(tmp_config_path: str, tmp_config_file_name: str):
    config = Configuration()
    new_default = {"env": {"test": "test"}}
    config.init_config(tmp_config_path, new_default, tmp_config_file_name)
    assert os.environ.get("ENV_TEST") == "test"

def test_nested_os_environment_variavles(tmp_config_path: str, tmp_config_file_name: str):
    config = Configuration()
    new_default = {"env": {"level1": {"level2": {"test": "test"}}}}
    config.init_config(tmp_config_path, new_default, tmp_config_file_name)
    assert os.environ.get("ENV_LEVEL1_LEVEL2_TEST") == "test"
    assert os.environ.get("ENV_LEVEL1_LEVEL2") is None
    
def test_os_environment_variables_with_prefix(config_instance_env_prefix: Configuration):
    assert os.environ.get("TEST_LOGGING_DEBUG") == "False"
    config_instance_env_prefix.logging.debug = True
    config_instance_env_prefix.update()
    assert os.environ.get("TEST_LOGGING_DEBUG") == "True"

def test_os_environment_override(default_config: dict[str, dict], tmp_config_path: str, tmp_config_file_name: str):
    os.environ["LOGGING_DEBUG"] = "Disabled"
    config = Configuration()
    config.init_config(tmp_config_path, default_config, tmp_config_file_name)
    assert config.logging_debug == "Disabled"
    assert config.logging.debug == "Disabled"
    assert config.config["logging"]["debug"] == "Disabled"

@pytest.fixture
def config_object():
    config = {
        "app": {
            "host": "localhost",
            "port": 8080
        },
        "logging": {
            "debug": False,
            "level": "info"
        }
    }
    return ConfigObject(config)

def test_config_object_attribute_access(config_object):
    assert config_object.app.host == "localhost"
    assert config_object.app.port == 8080
    assert config_object.logging.debug is False
    assert config_object.logging.level == "info"

def test_config_object_attribute_update(config_object):
    config_object.app.host = "test_localhost"
    config_object.app.port = 8888
    config_object.logging.debug = True
    config_object.logging.level = "debug"
    assert config_object.app.host == "test_localhost"
    assert config_object.app.port == 8888
    assert config_object.logging.debug is True
    assert config_object.logging.level == "debug"

def test_parse_env_value_true(config_instance: Configuration):
    values = ["true", "True", "TRUE"]
    for value in values:
        parsed_value = config_instance._parse_env_value(value)
        assert parsed_value is True

def test_parse_env_value_false(config_instance: Configuration):
    values = ["false", "False", "FALSE"]
    for value in values:
        parsed_value = config_instance._parse_env_value(value)
        assert parsed_value is False

def test_parse_env_value_integer(config_instance: Configuration):
    values = ["123000","123_000"]
    for value in values:
        parsed_value = config_instance._parse_env_value(value)
        assert parsed_value == 123000

def test_parse_env_value_float(config_instance: Configuration):
    value = "3.14"
    parsed_value = config_instance._parse_env_value(value)
    assert parsed_value == 3.14

def test_parse_env_value_string(config_instance: Configuration):
    value = "hello"
    parsed_value = config_instance._parse_env_value(value)
    assert parsed_value == "hello"

def test_parse_env_value_list(config_instance: Configuration):
    value = "[1, 2, 3]"
    parsed_value = config_instance._parse_env_value(value)
    assert parsed_value == [1, 2, 3]

def test_parse_env_value_dict(config_instance: Configuration):
    value = '{"key": "value"}'
    parsed_value = config_instance._parse_env_value(value)
    assert parsed_value == {"key": "value"}

def test_parse_env_value_datetime(config_instance: Configuration):
    value = "2022-01-01 00:00:00"
    parsed_value = config_instance._parse_env_value(value)
    assert isinstance(parsed_value, datetime)
    assert parsed_value.year == 2022
    assert parsed_value.month == 1
    assert parsed_value.day == 1
    assert parsed_value.hour == 0
    assert parsed_value.minute == 0
    assert parsed_value.second == 0

def test_parse_env_value_invalid(config_instance: Configuration):
    value = "normal string"
    parsed_value = config_instance._parse_env_value(value)
    assert parsed_value == "normal string"

def test_make_env_name_with_prefix(config_instance: Configuration):
    config_instance.env_prefix = "TEST"
    table = "logging"
    key = "debug"
    env_name = config_instance._make_env_name(table, key)
    assert env_name == "TEST_LOGGING_DEBUG"

def test_make_env_name_without_prefix(config_instance: Configuration):
    config_instance.env_prefix = None
    table = "app"
    key = "port"
    env_name = config_instance._make_env_name(table, key)
    assert env_name == "APP_PORT"