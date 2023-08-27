
from flask import Flask, jsonify, request, url_for,redirect
from extensions.config import settings
import logging

logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.config.get("app").get("flask_secret_key")
    app.config['APP_PORT'] = settings.config.get("app").get("port")
    app.config['APP_IP'] = settings.config.get("app").get("ip")
    app.config['APP_HOST'] = settings.config.get("app").get("host")
    app.config["DEBUG"] = settings.config.get("app").get("debug")
    return app

app = create_app()

# simple route that returns the config
@app.route("/")
def app_settings():
    return jsonify(
        {
        "response":  {
            "data": {
                "configuration": settings.get_settings(),
                "toml_config": settings.config,
            }
        }
        })

# Update settings route
@app.route("/update", methods=["POST"])
def update_settings():
    """Update settings route"""
    data = request.get_json() # {"logging_debug": True, "app_debug": True}
    settings.update_config(data)
    return redirect(url_for("app_settings"))

# Get settings value route
@app.route("/logger", methods=["GET"])
def get_settings():
    """Sets logging_debug to True or False"""
    value = False if settings.logging_debug else True
    settings.update_config({"logging_debug": value})
    return jsonify({"debug_logging": settings.logging_debug})

if __name__ == "__main__":
    app.run(port=app.config.get("APP_PORT"), host=app.config.get("APP_IP"), debug=app.config.get("APP_DEBUG"))
