class IOs(object):
    @staticmethod
    def read(path: str, encoding="utf-8") -> str:
        file = open(path, "r", encoding=encoding)
        content = file.read()
        file.close()
        return content

    @staticmethod
    def write(path: str, content: str, encoding="utf-8"):
        file = open(path, "w", encoding=encoding)
        file.write(content)
        file.close()
