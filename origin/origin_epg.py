
import fHDHR.tools


class OriginEPG():

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

    def duration_tvheadend_minutes(self, starttime, endtime):
        return ((int(endtime) - int(starttime))/60)

    def update_epg(self, fhdhr_channels):
        programguide = {}

        for fhdhr_id in list(fhdhr_channels.list.keys()):
            chan_obj = fhdhr_channels.list[fhdhr_id]

            if str(chan_obj.dict["number"]) not in list(programguide.keys()):
                programguide[str(chan_obj.dict["number"])] = chan_obj.epgdict

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

            chan_obj = fhdhr_channels.get_channel_obj("origin_number", progdict["channelNumber"])

            clean_prog_dict = {
                                "time_start": int(progdict["start"]),
                                "time_end": int(progdict["stop"]),
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
                                "id": str(progdict['id'] or "%s_%s" % (chan_obj.dict['origin_id'], progdict["start"])),
                                }

            if not any((d['time_start'] == clean_prog_dict['time_start'] and d['id'] == clean_prog_dict['id']) for d in programguide[chan_obj.number]["listing"]):
                programguide[str(chan_obj.dict["number"])]["listing"].append(clean_prog_dict)

        return programguide
