# Configuration settings for the cricket scraping application

import os
import json

class Config:
    def __init__(self):
        self.load_config()

    def load_config(self):
        config_file = os.getenv('CONFIG_FILE', 'config/default_config.json')
        with open(config_file, 'r') as f:
            config = json.load(f)
            self.api_key = config.get('API_KEY', '')
            self.base_url = config.get('BASE_URL', '')
            self.database_path = config.get('DATABASE_PATH', 'data/cricket_data.db')
            self.log_level = config.get('LOG_LEVEL', 'INFO')

    def __repr__(self):
        return f"<Config(api_key={self.api_key}, base_url={self.base_url}, database_path={self.database_path}, log_level={self.log_level})>"