
from .tvh_html import TVH_HTML


class Plugin_OBJ():

    def __init__(self, fhdhr, plugin_utils):
        self.fhdhr = fhdhr
        self.plugin_utils = plugin_utils

        self.tvh_html = TVH_HTML(fhdhr, plugin_utils)
