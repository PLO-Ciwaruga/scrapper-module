"""
    PLO-Ciwaruga

    Connector Module, Receiving Module
    23/05/2020
"""

import requests
import os
import random
import json
import shutil
from datetime import datetime


class Receiver:
    __resultDir: str
    __archiveDir: str
    __extractDir: str

    def __init__(self, labelUrl: str, tempDir: str):
        self.__archiveDir = self.__downloadData(labelUrl, tempDir)
        self.__extractDir = tempDir + '/' + str(random.randint(1000, 9999))

        if self.__archiveDir != None:
            os.mkdir(self.__extractDir)
            self.__extractData(self.__archiveDir, self.__extractDir)

            self.__resultDir = self.__extractDir + '/result.json'

    def __downloadData(self, labelUrl: str, tempDir: str):
        print('[INFO] Downloading data from label studio')
        req = requests.get(labelUrl + '/api/export?format=JSON_MIN')

        if req.status_code == 200:
            with open(tempDir + '/temp_archive.zip', 'wb+') as dest_file:
                dest_file.write(req.content)

            return tempDir + '/temp_archive.zip'
        else:
            return None

    def __extractData(self, archiveDir: str, extractDir: str):
        print('[INFO] Extracting data to %s' % (extractDir))
        shutil.unpack_archive(archiveDir, extract_dir=extractDir)

    def saveFile(self, saveDir: str):
        saveFileName = 'results-' + datetime.now().strftime('%d%b%Y-%H%M%S') + '.json'
        saveFileDir = saveDir + '/' + saveFileName

        print('[INFO] Moving result file into %s' % (saveFileDir))
        shutil.move(self.__resultDir, saveFileDir)

        os.remove(self.__archiveDir)
        shutil.rmtree(self.__extractDir)

        self.__resultDir = None
        self.__archiveDir = None
        self.__extractDir = None

        return saveFileDir