import os
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

def test_update_config(config_instance: Configuration):
    config_instance.config = TOMLDocument()
    config_instance.config["app"] = {
        "host": "localhost",
        "port": 8080
    }
    config_instance.update_config({"app_host": "test_localhost", "app_port": 8888})
    assert config_instance.config["app"]["host"] == "test_localhost"
    assert config_instance.config["app"]["port"] == 8888

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

def test_update_attribute(config_instance: Configuration, default_config: dict[str, dict]):
    config_instance.logging.debug = True
    config_instance.update()
    assert config_instance.logging_debug is True

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
