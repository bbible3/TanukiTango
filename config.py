import json


class TanukiTangoConfig:

    tesseract_executable = None
    language_mode = None
    config_file_location = None
    config = None

    #Init
    def __init__(self):
        self.config_file_location = "./tanukitango.json"
        self.config = self.loadConfig()
        self.tesseract_executable = None
        self.language_mode = None

        self.loadConfig()
    
    def asJson(self):
        jsonObj = {"tesseract_executable": self.tesseract_executable, "language_mode": self.language_mode}
        return json.dumps(jsonObj)
    
    def saveConfig(self):
        if self.config_file_location:
            with open(self.config_file_location, "w") as f:
                f.write(self.asJson())
        else:
            #Create a new config file
            with open("tanukitango.json", "w") as f:
                f.write(self.asJson())
    #Try to load tanukitango.json
    def loadConfig(self):
        print("Loading config")
        try:
            with open("tanukitango.json", "r") as f:
                print("Loading config from tanukitango.json")
                from_file_config = json.load(f)
                #Does json have key tesseract_executable?
                if "tesseract_executable" in from_file_config:
                    self.tesseract_executable = from_file_config["tesseract_executable"]
                else:
                    self.tesseract_executable = None
                if "language_mode" in from_file_config:
                    self.language_mode = from_file_config["language_mode"]
                else:
                    self.language_mode = None
        except Exception as e:
            print("Could not load config from tanukitango.json", e)
            #Create
            print("Creating empty config")
            self.tesseract_executable = None
            self.language_mode = None
            self.saveConfig()

    def setLanguageMode(self, mode):
        self.language_mode = mode
        self.saveConfig()