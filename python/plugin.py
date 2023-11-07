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


class DataReaderPluginManager(PluginManager):
    def reader(self, name, data):
        return self.plugins.get(name).reader(data)


class DataProcessPluginManager(PluginManager):
    def process(self, name, data):
        return self.plugins.get(name).process(data)


class DataFeaturePluginManager(PluginManager):
    def feature(self, name, data):
        return self.plugins.get(name).process(data)


if __name__ == "__main__":
    sys.path.insert(0, './plugins')
    md = importlib.import_module('test')
    pm = PluginManager()
    pm.register('test', md)

    module = pm.get_plugin('test')
    print(dir(module))
