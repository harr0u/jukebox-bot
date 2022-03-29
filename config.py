import json


class Config:
    def __init__(self, path: str):
        with open(path, 'r') as f:
            self.values = json.load(f)
