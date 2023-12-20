import sys
import importlib


class PluginManager:
    def __init__(self):
        print("PluginManager init")
        self.plugins = {}

    def register(self, name, plugin):
        # # Add a new plugin
        self.plugins[name] = plugin

    def get_plugin(self, name):
        # Return a specific plugin
        return self.plugins.get(name)

    def del_plugin(self, name):
        # Remove a specific plugin
        del self.plugins[name]

    def list_plugin(self):
        # Return a list of all the plugins
        return self.plugins.keys()


PM = PluginManager()
