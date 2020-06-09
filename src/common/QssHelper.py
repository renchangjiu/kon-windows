from src.component.Const import Const


class QssHelper(object):

    @staticmethod
    def load(relative_path: str) -> str:
        """ 加载 qss 资源文件。

        :param relative_path: 以 /resource/qss/ 为根目录的相对路径
        """
        path = Const.rp("/qss%s" % relative_path)
        file = open(path, "r", encoding="utf-8")
        content = file.read()
        file.close()
        p = Const.res + "/"
        return content.replace("/resource/", p)
