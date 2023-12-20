import sys
import importlib


class PluginManager:
    def __init__(self):
        print("PluginManager init")
        self.plugins = {}

    def register(self, name, plugin):
        self.plugins[name] = plugin

    def get_plugin(self, name):
        return self.plugins.get(name)

    def del_plugin(self, name):
        del self.plugins[name]

    def list_plugin(self):
        return self.plugins.keys()


PM = PluginManager()
