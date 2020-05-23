"""
    PLO-Ciwaruga

    Params Module
    22/05/2020
"""
import json
import os


class Params:
    path: str
    n_kompas: int
    n_detik: int
    n_republika: int
    label_studio_url: str
    chrome_driver_path: str
    chrome_bin_path: str
    temp_dir: str
    result_dir: str

    def __init__(self, path: str = 'params.json') -> None:
        print('[INFO] Loading parameters from file')
        self.path = path
        try:
            with open(path, 'r') as source_file:
                rawDict = json.load(source_file)

            self.n_kompas = rawDict['nKompas']
            self.n_detik = rawDict['nDetik']
            self.n_republika = rawDict['nRepublika']
            self.label_studio_url = rawDict['labelStudioURL']
            self.chrome_driver_path = rawDict['chromeWebDriverPath']
            self.chrome_bin_path = rawDict['chromeBinPath']
            self.temp_dir = rawDict['tempDir']
            self.result_dir = rawDict['resDir']

        except json.JSONDecodeError as JDE:
            print('[ERROR] Params file opening error ', JDE)
            print('[INFO] Will create a new empty (default) settings')

            settings = {
                "nKompas": 10,
                "nDetik": 10,
                "nRepublika": 10,
                "labelStudioURL": "",
                "chromeWebDriverPath": "",
                "chromeBinPath": "",
                "tempDir": os.getcwd() + "/tmp",
                "resDir": os.getcwd() + "/res"
            }

            with open(path, 'w') as dest_file:
                json.dump(settings, dest_file)
                dest_file.close()

            print('[INFO] Loading parameters from file')
            with open(path, 'r') as source_file:
                rawDict = json.load(source_file)

    def update(self) -> None:
        print('[INFO] Updating the parameters')
        settings = {
            "nKompas": self.n_kompas,
            "nDetik": self.n_detik,
            "nRepublika": self.n_republika,
            "labelStudioURL": self.label_studio_url,
            "chromeWebDriverPath": self.chrome_driver_path,
            "chromeBinPath": self.chrome_bin_path,
            "tempDir": self.temp_dir,
            "resDir": self.result_dir
        }

        with open(self.path, 'w') as dest_file:
            json.dump(settings, dest_file)

    def getEnvSettings(self) -> None:
        print('[INFO] Getting ENV settings')
        temp_driver_path = os.getenv('GOOGLE_CHROME_BIN')
        temp_bin_path = os.getenv('CHROMEDRIVER_PATH')

        if temp_bin_path != None and temp_driver_path != None:
            self.chrome_bin_path = temp_bin_path
            self.chrome_driver_path = temp_driver_path

            self.update()
        else:
            print('[INFO] No ENV settings found, using params file instead')
