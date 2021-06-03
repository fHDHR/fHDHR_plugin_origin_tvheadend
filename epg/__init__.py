from simplejson import errors as simplejsonerrors

import fHDHR.tools


class Plugin_OBJ():

    def __init__(self, channels, plugin_utils):
        self.plugin_utils = plugin_utils

        self.channels = channels

        self.origin = plugin_utils.origin

    def duration_tvheadend_minutes(self, starttime, endtime):
        return ((int(endtime) - int(starttime))/60)

    def update_epg(self):
        programguide = {}

        for fhdhr_id in list(self.channels.list[self.plugin_utils.namespace].keys()):
            chan_obj = self.channels.list[self.plugin_utils.namespace][fhdhr_id]

            if str(chan_obj.number) not in list(programguide.keys()):
                programguide[str(chan_obj.number)] = chan_obj.epgdict

        epg_url = ('%s%s:%s@%s:%s/api/epg/events/grid?limit=999999' %
                   ("https://" if self.plugin_utils.config.dict['tvheadend']["ssl"] else "http://",
                    self.plugin_utils.config.dict['tvheadend']["username"],
                    self.plugin_utils.config.dict['tvheadend']["password"],
                    self.plugin_utils.config.dict['tvheadend']["address"],
                    str(self.plugin_utils.config.dict['tvheadend']["port"]),
                    ))
        r = self.plugin_utils.web.session.get(epg_url)
        try:
            entries = r.json()['entries']
        except simplejsonerrors.JSONDecodeError as err:
            self.plugin_utils.logger.error("EPG Gathering Failed: %s" % err)
            return programguide

        for program_item in entries:

            progdict = fHDHR.tools.xmldictmaker(program_item, ["channelNumber", "start", "stop", "eventId", "title", "name", "subtitle", "rating", "description", "season", "episode", "id", "episodeTitle"])

            chan_obj = self.channels.get_channel_obj("origin_number", progdict["channelNumber"], self.plugin_utils.namespace)

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
                programguide[str(chan_obj.number)]["listing"].append(clean_prog_dict)

        return programguide
