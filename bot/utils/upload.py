from utils.logger import log
from config import PATH

class UploadPic():
    __src: str 


    def __init__(self, src: str) -> None:
        self.__src = src


    def upload(self, file, file_info) -> None:
        """
        Upload only photo in cause of telegram saving new photos to default folder "photos/"
        """
        log.info("UploadPic -- Загрузка файла на сервер")
        source_file_name = self.__src + file_info.file_path.replace('photos/', '')
        with open(source_file_name, 'wb') as new_file:
            new_file.write(file)
        log.info("Успешно")


