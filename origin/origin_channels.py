

class OriginChannels():

    def __init__(self, fhdhr, origin):
        self.fhdhr = fhdhr
        self.origin = origin

    def get_channels(self):

        r = self.fhdhr.web.session.get(('%s%s:%s@%s:%s/api/channel/grid?start=0&limit=999999' %
                                       ("https://" if self.fhdhr.config.dict['origin']["ssl"] else "http://",
                                        self.fhdhr.config.dict['origin']["username"],
                                        self.fhdhr.config.dict['origin']["password"],
                                        self.fhdhr.config.dict['origin']["address"],
                                        str(self.fhdhr.config.dict['origin']["port"]))))
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
                     ("https://" if self.fhdhr.config.dict['origin']["ssl"] else "http://",
                      self.fhdhr.config.dict['origin']["username"],
                      self.fhdhr.config.dict['origin']["password"],
                      self.fhdhr.config.dict['origin']["address"],
                      str(self.fhdhr.config.dict['origin']["port"]),
                      str(chandict["origin_id"]),
                      streamprofile,
                      int(self.fhdhr.config.dict["origin"]['weight'])
                      ))

        stream_info = {"url": streamurl}

        return stream_info
