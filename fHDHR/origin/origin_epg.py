import datetime

import fHDHR.tools


class OriginEPG():

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

    def xmltimestamp_tvheadend(self, epochtime):
        xmltime = datetime.datetime.fromtimestamp(int(epochtime))
        xmltime = str(xmltime.strftime('%Y%m%d%H%M%S')) + " +0000"
        return xmltime

    def duration_tvheadend_minutes(self, starttime, endtime):
        return ((int(endtime) - int(starttime))/60)

    def update_epg(self, fhdhr_channels):
        programguide = {}

        for c in fhdhr_channels.get_channels():

            cdict = fHDHR.tools.xmldictmaker(c, ["callsign", "name", "number", "id"])

            if str(cdict['number']) not in list(programguide.keys()):

                programguide[str(cdict['number'])] = {
                                                    "callsign": cdict["callsign"],
                                                    "name": cdict["name"] or cdict["callsign"],
                                                    "number": cdict["number"],
                                                    "id": str(cdict["origin_id"]),
                                                    "thumbnail": None,
                                                    "listing": [],
                                                    }

        epg_url = ('%s%s:%s@%s:%s/api/epg/events/grid?limit=999999' %
                   ("https://" if self.fhdhr.config.dict['origin']["ssl"] else "http://",
                    self.fhdhr.config.dict['origin']["username"],
                    self.fhdhr.config.dict['origin']["password"],
                    self.fhdhr.config.dict['origin']["address"],
                    str(self.fhdhr.config.dict['origin']["port"]),
                    ))
        r = self.fhdhr.web.session.get(epg_url)
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
