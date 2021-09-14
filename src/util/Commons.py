from pydub import AudioSegment

""" 一般工具集合 """


class Commons:

    @staticmethod
    def export2wave(src: str, dest: str):
        """ 调用 pydub 库, 把任意格式的音频文件转成 wav 格式

        :param src: 源文件全路径
        :param dest: 目标文件全路径
        """
        print("pydub: ", src, " -->", dest)
        AudioSegment.from_file(src).export(dest, format="wav")
