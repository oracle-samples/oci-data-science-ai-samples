"""Flask app with /health and /predict endpoint."""

import importlib.util
import logging
import os
import sys
import traceback

from flask import Flask, request


# Get logging and debugging settings from environment variables
LOG_LEVEL = os.environ.get("LOG_LEVEL", logging.INFO)
MODEL_DIR = os.environ.get("MODEL_DIR", "/opt/ds/model/deployed_model")
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", False)


def set_log_level(the_logger: logging.Logger, log_level=None):
    """Sets the log level of a logger based on the environment variable.
    This will also set the log level of logging.lastResort.
    """
    if not log_level:
        return the_logger
    try:
        the_logger.setLevel(log_level)
        logging.lastResort.setLevel(log_level)
        the_logger.info(f"Log level set to {log_level}")
    except Exception:
        # Catching all exceptions here
        # Setting log level should not interrupt the job run even if there is an exception.
        the_logger.warning("Failed to set log level.")
        the_logger.debug(traceback.format_exc())
    return the_logger


def import_from_path(file_path, module_name="score"):
    """Imports a module from file path."""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


logger = logging.getLogger(__name__)
set_log_level(logger, LOG_LEVEL)

score = import_from_path(os.path.join(MODEL_DIR, "score.py"))
app = Flask(__name__)


@app.route("/health")
def health():
    """Health check."""
    return {"status": "success"}


@app.route("/predict", methods=["POST"])
def predict():
    """Make prediction."""
    payload = request.get_data()
    results = score.predict(payload)
    return results


if __name__ == "__main__":
    app.run(debug=FLASK_DEBUG, host="0.0.0.0", port=8080)
