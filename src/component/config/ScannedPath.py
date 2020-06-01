from src.component.config.BaseConfig import BaseConfig


class ScannedPath(BaseConfig):

    def __init__(self, path: str, checked: bool) -> None:
        self.path = path
        self.checked = checked

    @staticmethod
    def add(scp, scps: list):
        for scp_ in scps:
            if scp_.path == scp.path:
                return
        scps.append(scp)

    @staticmethod
    def parse(json_obj) -> list:
        res = []
        paths_ = json_obj["scannedPaths"]
        for o in paths_:
            res.append(ScannedPath(o["path"], o["checked"]))
        return res

    @staticmethod
    def stringify(part_config):
        res = []
        for sp in part_config:
            res.append({
                "path": sp.path,
                "checked": sp.checked
            })
        return res
