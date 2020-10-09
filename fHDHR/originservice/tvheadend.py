import json
import datetime

import fHDHR.tools


class fHDHRservice():
    def __init__(self, settings):
        self.config = settings

        self.web = fHDHR.tools.WebReq()

    def login(self):
        return True

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

    def update_epg(self):
        programguide = {}

        for c in self.get_channels():

            cdict = fHDHR.tools.xmldictmaker(c, ["callsign", "name", "number", "id"])

            if str(cdict['number']) not in list(programguide.keys()):

                programguide[str(cdict['number'])] = {
                                                    "callsign": cdict["callsign"],
                                                    "name": cdict["name"] or cdict["callsign"],
                                                    "number": cdict["number"],
                                                    "id": str(cdict["id"]),
                                                    "thumbnail": None,
                                                    "listing": [],
                                                    }

        epg_url = ('%s%s:%s@%s:%s/api/epg/events/grid?limit=999999' %
                   ("https://" if self.config.dict['origin']["ssl"] else "http://",
                    self.config.dict['origin']["username"],
                    self.config.dict['origin']["password"],
                    self.config.dict['origin']["address"],
                    str(self.config.dict['origin']["port"]),
                    ))
        r = self.web.session.get(epg_url)
        entries = r.json()['entries']

        for program_item in entries:

            progdict = fHDHR.tools.xmldictmaker(program_item, ["channelNumber", "start", "stop", "eventId", "title", "name", "subtitle", "rating", "description", "season", "episode", "id", "episodeTitle"])

            clean_prog_dict = {
                                "time_start": self.xmltimestamp_tvheadend(progdict["start"]),
                                "time_end": self.xmltimestamp_tvheadend(progdict["stop"]),
                                "duration_minutes": self.duration_tvheadend_minutes(progdict["start"], progdict["stop"]),
                                "thumbnail": None,
                                "title": progdict['title'] or "Unavailable",
                                "sub-title": progdict['subtitle'] or "Unavailable",
                                "description": progdict['description'] or "Unavailable",
                                "rating": progdict['rating'] or "N/A",
                                "episodetitle": progdict['episodeTitle'],
                                "releaseyear": None,
                                "genres": [],
                                "seasonnumber": progdict['season'],
                                "episodenumber": progdict['episode'],
                                "isnew": False,
                                "id": str(progdict['eventId'] or self.xmltimestamp_tvheadend(progdict["start"])),
                                }

            programguide[str(progdict["channelNumber"])]["listing"].append(clean_prog_dict)

        return programguide

    def xmltimestamp_tvheadend(self, epochtime):
        xmltime = datetime.datetime.fromtimestamp(int(epochtime))
        xmltime = str(xmltime.strftime('%Y%m%d%H%M%S')) + " +0000"
        return xmltime

    def duration_tvheadend_minutes(self, starttime, endtime):
        return ((int(endtime) - int(starttime))/60)
