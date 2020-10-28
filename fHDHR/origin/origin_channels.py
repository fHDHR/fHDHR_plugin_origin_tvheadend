import json

import fHDHR.tools


class OriginService():

    def __init__(self, settings):
        self.config = settings

        self.web = fHDHR.tools.WebReq()

    def get_status_dict(self):
        ret_status_dict = {}
        return ret_status_dict

    def get_channels(self):

        # otherwise we get an undefined error loading the dict
        true = True
        true

        r = self.web.session.get(('%s%s:%s@%s:%s/api/channel/grid?start=0&limit=999999' %
                                 ("https://" if self.config.dict['origin']["ssl"] else "http://",
                                  self.config.dict['origin']["username"],
                                  self.config.dict['origin']["password"],
                                  self.config.dict['origin']["address"],
                                  str(self.config.dict['origin']["port"]))))

        channel_list = []
        for c in r.json()['entries']:
            dString = json.dumps(c)
            channel_dict = eval(dString)
            clean_station_item = {
                                 "name": channel_dict["name"],
                                 "callsign": channel_dict["name"],
                                 "number": channel_dict["number"],
                                 "id": channel_dict["uuid"],
                                 }
            channel_list.append(clean_station_item)
        return channel_list

    def get_channel_stream(self, chandict, allchandict):
        caching = True
        streamlist = []
        streamdict = {}
        streamurl = ('%s%s:%s@%s:%s/stream/channel/%s?profile=%s&weight=%s' %
                     ("https://" if self.config.dict['origin']["ssl"] else "http://",
                      self.config.dict['origin']["username"],
                      self.config.dict['origin']["password"],
                      self.config.dict['origin']["address"],
                      str(self.config.dict['origin']["port"]),
                      str(chandict["id"]),
                      self.config.dict["origin"]['streamprofile'],
                      int(self.config.dict["origin"]['weight'])
                      ))
        streamdict = {"number": chandict["number"], "stream_url": streamurl}
        streamlist.append(streamdict)
        return streamlist, caching
