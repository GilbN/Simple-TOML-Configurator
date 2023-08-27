class TOMLConfiguratorException(Exception):
    """Base class for all exceptions raised by the TomlConfigurator class."""
    pass

class TOMLConfigUpdateError(TOMLConfiguratorException):
    """Raised when an error occurs while updating the TOML configuration file."""
    pass

class TOMLWriteConfigError(TOMLConfiguratorException):
    """Raised when an error occurs while writing the TOML configuration file."""
    pass

class TOMLConfigFileNotFound(TOMLConfiguratorException):
    """Raised when the TOML configuration file is not found."""
    pass

class TOMLCreateConfigError(TOMLConfiguratorException):
    """Raised when an error occurs while creating the TOML configuration file."""
    pass

class  TOMLLoadConfigError(TOMLConfiguratorException):
    """Raised when an error occurs while loading the TOML configuration file."""
    pass