from ajenti.api import *
from ajenti.plugins import *


info = PluginInfo(
    title='Firewall',
    dependencies=[
        PluginDependency('main')
    ],
)


def init():
    import main
