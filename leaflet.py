import datetime

class Leaflet:

    def __init__(self,title,thumbnail,shop_name,valid_from,valid_to,parsed_time=None):
        self.title = title
        self.thumbnail = thumbnail
        self.shop_name = shop_name
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.parsed_time = parsed_time if parsed_time is not None else datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")

    def to_dict(self):
        return {
            "title": self.title,
            "thumbnail": self.thumbnail,
            "shop_name": self.shop_name,
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "parsed_time": self.parsed_time
        }

