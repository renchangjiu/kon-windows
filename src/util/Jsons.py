import json


class Jsons(object):

    @staticmethod
    def dumps(obj: object) -> str:
        """ Obj to json. """
        return json.dumps(obj, ensure_ascii=False)

    @staticmethod
    def loads(json_str: str) -> object:
        """ Json to obj. """
        return json.loads(json_str, ensure_ascii=False)
