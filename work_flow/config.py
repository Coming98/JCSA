
import json

def init_config(self):
    self.dict_name = None  
    
def save_config(self):
    config = {
        'dict_name': self.dict_name
    }
    with open(self.config_path, 'w') as f:
        json.dump(config, f)

def load_config(self):
    with open(self.config_path, 'r') as f:
        config = json.load(f)
    return config