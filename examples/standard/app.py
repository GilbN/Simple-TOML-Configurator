
from flask import Flask, jsonify, request, url_for,redirect
from extenstions.config import settings

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
            }
            }
        })

# Update settings route
@app.route("/update", methods=["POST"])
def update_settings():
    data = request.get_json() # {"app_proxy": "http://localhost:8080", "app_debug": "True}
    settings.update_config(data)
    return redirect(url_for("app_settings"))

# Get settings value route
@app.route("/get", methods=["GET"])
def get_settings():
    key = request.args.get("key","")
    value = request.args.get("value","")
    config_attr_value = settings.config.get(key, {}).get(value, "not found")
    instance_attr_value = getattr(settings, key, "not found")
    return jsonify(
        {
        "response":  {
            "data": {
                "Configuration.config": {
                "key": key,
                "value": config_attr_value,
                },
                "Configuration": {
                "key": key,
                "value": instance_attr_value,
                },
            }
            }
        })

if __name__ == "__main__":
    app.run(port=app.config.get("APP_PORT"), host=app.config.get("APP_IP"), debug=app.config.get("APP_DEBUG"))
