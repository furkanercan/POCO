import json5
import os

# Load configuration from config.json
config_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json5')
with open(config_file_path, 'r') as f:
    config_data = json5.load(f)

# Expose the configuration data as a global variable
CONFIG = config_data.get("simulation", {})
