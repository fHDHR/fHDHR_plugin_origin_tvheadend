import os
import json
import requests
import datetime


def xmldictmaker(inputdict, req_items, list_items=[], str_items=[]):
    xml_dict = {}

    for origitem in list(inputdict.keys()):
        xml_dict[origitem] = inputdict[origitem]

    for req_item in req_items:
        if req_item not in list(inputdict.keys()):
            xml_dict[req_item] = None
        if not xml_dict[req_item]:
            if req_item in list_items:
                xml_dict[req_item] = []
            elif req_item in str_items:
                xml_dict[req_item] = ""

    return xml_dict


def xmltimestamp_tvheadend(epochtime):
    xmltime = datetime.datetime.fromtimestamp(int(epochtime))
    xmltime = str(xmltime.strftime('%Y%m%d%H%M%S')) + " +0000"
    return xmltime


def duration_tvheadend_minutes(starttime, endtime):
    return ((int(endtime) - int(starttime))/60)


class proxyserviceFetcher():

    def __init__(self, config):
        self.config = config.copy()

        self.epg_cache = None
        self.epg_cache_file = self.config["proxy"]["epg_cache"]

        self.urls = {}
        self.url_assembler()

        self.epg_cache = self.epg_cache_open()

    def epg_cache_open(self):
        epg_cache = None
        if os.path.isfile(self.epg_cache_file):
            with open(self.epg_cache_file, 'r') as epgfile:
                epg_cache = json.load(epgfile)
        return epg_cache

    def thumb_url(self, thumb_type, base_url, thumbnail):
        if thumb_type == "channel":
            return "http://" + str(base_url) + str(thumbnail)
        elif thumb_type == "content":
            return "http://" + str(base_url) + str(thumbnail)

    def url_assembler(self):

        self.urls["channels"] = ('%s%s:%s@%s:%s/api/channel/grid?start=0&limit=999999' %
                                 ("https://" if self.config['proxy']["ssl"] else "http://",
                                  self.config['proxy']["username"],
                                  self.config['proxy']["password"],
                                  self.config['proxy']["address"],
                                  str(self.config['proxy']["port"])))

    def get_channels(self):

        # otherwise we get an undefined error loading the dict
        true = True
        true

        try:
            r = requests.get(self.urls["channels"])

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

        except Exception as e:
            print('An error occured: ' + repr(e))
            return []

    def get_station_list(self, base_url):
        station_list = []

        for c in self.get_channels():
            if self.config["fakehdhr"]["stream_type"] == "ffmpeg":
                watchtype = "ffmpeg"
            else:
                watchtype = "direct"
            url = ('%s%s/watch?method=%s&channel=%s' %
                   ("http://",
                    base_url,
                    watchtype,
                    c['id']
                    ))
            station_list.append(
                                {
                                 'GuideNumber': str(c['number']),
                                 'GuideName': c['name'],
                                 'URL': url
                                })
        return station_list

    def get_station_total(self):
        total_channels = 0
        for c in self.get_channels():
            total_channels += 1
        return total_channels

    def get_channel_stream(self, id):
        url = ('%s%s:%s@%s:%s/stream/channel/%s?profile=%s&weight=%s' %
               ("https://" if self.config['proxy']["ssl"] else "http://",
                self.config['proxy']["username"],
                self.config['proxy']["password"],
                self.config['proxy']["address"],
                str(self.config['proxy']["port"]),
                id,
                self.config["proxy"]['streamprofile'],
                int(self.config["proxy"]['weight'])
                ))
        return url

    def get_channel_streams(self):
        streamdict = {}
        for c in self.get_channels():
            if c['enabled']:
                url = ('%s%s:%s@%s:%s/stream/channel/%s?profile=%s&weight=%s' %
                       ("https://" if self.config['proxy']["ssl"] else "http://",
                        self.config['proxy']["username"],
                        self.config['proxy']["password"],
                        self.config['proxy']["address"],
                        str(self.config['proxy']["port"]),
                        c['uuid'],
                        self.config["proxy"]['streamprofile'],
                        int(self.config["proxy"]['weight'])
                        ))
                streamdict[str(c["number"])] = url
        return streamdict

    def get_channel_thumbnail(self, channel_id):
        channel_thumb_url = ("/images?source=empty&type=channel&id=%s" % (str(channel_id)))
        return channel_thumb_url

    def get_content_thumbnail(self, content_id):
        item_thumb_url = ("/images?source=empty&type=content&id=%s" % (str(content_id)))
        return item_thumb_url

    def update_epg(self):
        print('Updating Tvheadend EPG cache file.')

        programguide = {}

        for c in self.get_channels():

            cdict = xmldictmaker(c, ["callsign", "name", "number", "id"])

            if str(cdict['number']) not in list(programguide.keys()):

                programguide[str(cdict['number'])] = {
                                                    "callsign": cdict["callsign"],
                                                    "name": cdict["name"] or cdict["callsign"],
                                                    "number": cdict["number"],
                                                    "id": cdict["id"],
                                                    "thumbnail": ("/images?source=proxy&type=channel&id=%s" % (str(cdict['id']))),
                                                    "listing": [],
                                                    }

        epg_url = ('%s%s:%s@%s:%s/api/epg/events/grid?limit=999999' %
                   ("https://" if self.config['proxy']["ssl"] else "http://",
                    self.config['proxy']["username"],
                    self.config['proxy']["password"],
                    self.config['proxy']["address"],
                    str(self.config['proxy']["port"]),
                    ))
        r = requests.get(epg_url)
        entries = r.json()['entries']

        for program_item in entries:

            progdict = xmldictmaker(program_item, ["channelNumber", "start", "stop", "eventId", "title", "name", "subtitle", "rating", "description", "season", "episode", "id", "episodeTitle"])

            clean_prog_dict = {
                                "time_start": xmltimestamp_tvheadend(progdict["start"]),
                                "time_end": xmltimestamp_tvheadend(progdict["stop"]),
                                "duration_minutes": duration_tvheadend_minutes(progdict["start"], progdict["stop"]),
                                "thumbnail": ("/images?source=proxy&type=content&id=%s" % (str(progdict['id']))),
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
                                "id": progdict['eventId'] or xmltimestamp_tvheadend(progdict["start"]),
                                }

            programguide[str(progdict["channelNumber"])]["listing"].append(clean_prog_dict)

        self.epg_cache = programguide
        with open(self.epg_cache_file, 'w') as epgfile:
            epgfile.write(json.dumps(programguide, indent=4))
        print('Wrote updated Tvheadend EPG cache file.')
        return programguide
