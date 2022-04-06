import json
from simplejson import errors as simplejsonerrors


class Plugin_OBJ():

    def __init__(self, plugin_utils):
        self.plugin_utils = plugin_utils

    @property
    def webpage_dict(self):
        return {
                "Address": self.address_without_creds,
                "Username": self.username,
                }

    @property
    def username(self):
        return self.plugin_utils.config.dict["tvheadend"]["username"]

    @property
    def password(self):
        return self.plugin_utils.config.dict["tvheadend"]["password"]

    @property
    def address(self):
        return self.plugin_utils.config.dict["tvheadend"]["address"]

    @property
    def port(self):
        return self.plugin_utils.config.dict["tvheadend"]["port"]

    @property
    def weight(self):
        return self.plugin_utils.config.dict["tvheadend"]["weight"]

    @property
    def proto(self):
        return "https://" if self.plugin_utils.config.dict['tvheadend']["ssl"] else "http://"

    @property
    def address_with_creds(self):
        return '%s%s:%s@%s:%s' % (self.proto, self.username, self.password, self.address, str(self.port))

    @property
    def address_without_creds(self):
        return '%s%s:%s' % (self.proto, self.address, str(self.port))

    def get_channels(self):

        r = self.plugin_utils.web.session.get('%s/api/channel/grid?start=0&limit=999999' % self.address_with_creds)

        try:
            entries = r.json()['entries']
        except json.JSONDecodeError as err:
            self.plugin_utils.logger.error("Channel Gathering Failed: %s" % err)
            return []
        except simplejsonerrors.JSONDecodeError as err:
            self.plugin_utils.logger.error("Channel Gathering Failed: %s" % err)
            return []

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
        elif stream_args["origin_quality"]:
            streamprofile = stream_args["origin_quality"]
        else:
            streamprofile = "pass"

        streamurl = ('%s/stream/channel/%s?profile=%s&weight=%s' % (self.address_with_creds, chandict["origin_id"], streamprofile, self.weight))

        stream_info = {"url": streamurl}

        return stream_info
