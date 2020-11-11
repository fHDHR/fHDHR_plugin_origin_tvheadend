

class OriginService():

    def __init__(self, fhdhr):
        self.fhdhr = fhdhr

    def get_status_dict(self):
        tvh_address = '%s%s:%s' % (
                                    "https://" if self.fhdhr.config.dict['origin']["ssl"] else "http://",
                                    self.fhdhr.config.dict['origin']["address"],
                                    str(self.fhdhr.config.dict['origin']["port"]))
        ret_status_dict = {
                            "Address": tvh_address,
                            "Username": self.fhdhr.config.dict['origin']["username"],
                            }
        return ret_status_dict
