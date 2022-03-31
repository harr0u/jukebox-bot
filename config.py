import os

class Config:
    def __getattr__(self, item):
        self.__dict__[item] = os.environ.get(item)
        return self.__dict__.get(item)
