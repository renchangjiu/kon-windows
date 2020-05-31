class ScannedPath(object):

    def __init__(self) -> None:
        # 具体路径
        self.path = ""

        # 是否勾选
        self.checked = False

    def __str__(self) -> str:
        return "(%s, %s)" % (self.path, self.checked)
