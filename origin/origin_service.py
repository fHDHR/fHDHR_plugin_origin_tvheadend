

class OriginService():

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

        self.tvh_address = ('%s%s:%s' %
                            ("https://" if self.fhdhr.config.dict['origin']["ssl"] else "http://",
                             self.fhdhr.config.dict['origin']["address"],
                             str(self.fhdhr.config.dict['origin']["port"])))
