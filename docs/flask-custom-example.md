# Custom Flask Example

The `Configuration` class can be extended and customized to cater to application-specific requirements. Developers can implement custom logic with getters and setters to handle unique settings or scenarios.

## Folder contents

```
├── __init__.py
├── app.py
├── utils.py
└── extensions
    └── config.py
```

This example uses a custom Configuration class in the config.py module that inherits from `Configuration`.

??? example "CustomConfiguration"
    ```python
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
    ```

The custom class uses a property with a setter that executes the `configure_logging` function from `utils.py` whenever the logging_debug attribute is updated. Thus setting the log level to "DEBUG" if the value is True.

This will change the log level on you Flask app without restarting it.

### Code examples

??? example "extensions/config.py"
    ```python title="config.py"
    --8<-- "examples/custom/extensions/config.py"
    ```

??? example "utils.py"
    ```python title="utils.py"
    --8<-- "examples/custom/utils.py"
    ```

!!! example "app.py"
    ```python title="app.py"
    --8<-- "examples/custom/app.py"
    ```