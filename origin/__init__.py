

class Plugin_OBJ():

    def __init__(self, plugin_utils):
        self.plugin_utils = plugin_utils

        self.tvh_address = ('%s%s:%s' %
                            ("https://" if self.plugin_utils.config.dict['tvheadend']["ssl"] else "http://",
                             self.plugin_utils.config.dict['tvheadend']["address"],
                             str(self.plugin_utils.config.dict['tvheadend']["port"])))

    def get_channels(self):

        r = self.plugin_utils.web.session.get(('%s%s:%s@%s:%s/api/channel/grid?start=0&limit=999999' %
                                              ("https://" if self.plugin_utils.config.dict['tvheadend']["ssl"] else "http://",
                                               self.plugin_utils.config.dict['tvheadend']["username"],
                                               self.plugin_utils.config.dict['tvheadend']["password"],
                                               self.plugin_utils.config.dict['tvheadend']["address"],
                                               str(self.plugin_utils.config.dict['tvheadend']["port"]))))
        entries = r.json()['entries']

        channel_list = []
        for channel_dict in entries:

            clean_station_item = {
                                 "name": channel_dict["name"],
                                 "callsign": channel_dict["name"],
                                 "number": channel_dict["number"],
                                 "id": channel_dict["uuid"],
                                 }
            try:
                thumbnail = channel_dict["icon"]
            except KeyError:
                thumbnail = None
            clean_station_item["thumbnail"] = thumbnail
            channel_list.append(clean_station_item)
        return channel_list

    def get_channel_stream(self, chandict, stream_args):
        if not stream_args["origin_quality"] or stream_args["origin_quality"] in ["high", "pass"]:
            streamprofile = "pass"
        else:
            streamprofile = "pass"

        streamurl = ('%s%s:%s@%s:%s/stream/channel/%s?profile=%s&weight=%s' %
                     ("https://" if self.plugin_utils.config.dict['tvheadend']["ssl"] else "http://",
                      self.plugin_utils.config.dict['tvheadend']["username"],
                      self.plugin_utils.config.dict['tvheadend']["password"],
                      self.plugin_utils.config.dict['tvheadend']["address"],
                      str(self.plugin_utils.config.dict['tvheadend']["port"]),
                      str(chandict["origin_id"]),
                      streamprofile,
                      int(self.plugin_utils.config.dict["tvheadend"]['weight'])
                      ))

        stream_info = {"url": streamurl}

        return stream_info
