

class OriginService():

    def __init__(self, settings, logger, web):
        self.config = settings
        self.logger = logger
        self.web = web

    def get_status_dict(self):
        tvh_address = '%s%s:%s' % (
                                    "https://" if self.config.dict['origin']["ssl"] else "http://",
                                    self.config.dict['origin']["address"],
                                    str(self.config.dict['origin']["port"]))
        ret_status_dict = {
                            "Address": tvh_address,
                            "Username": self.config.dict['origin']["username"],
                            }
        return ret_status_dict
