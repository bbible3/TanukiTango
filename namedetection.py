import regex
from enum import Enum
class TanukiNamer:
    #This experimental feature tries to automatically detect names and their readings from subtitles.
    #It is possible this will generate erronious results, or will require modification of your *.csv files after.
    #It is recommended to only use this if you know what you are doing.
    #This tool uses PyPi Regex. The default regular expression will detect names in these formats:
    #"（和也）" via regex: '.\p{Han}{2,4}.'
    #"（麻美(まみ)）" via regex: '.\p{Han}{2,4}.\p{Hiragana}+..'
    #You can customise the regex used to allow for more flexible detection.
    #Names will be automatically filtered against words in Genki.
    #Only kanji names will be included with the default regex.
    #If you want to be extra bold, enable the "unlikely names" feature.
    #By default, words that match the regex but are used very infrequently or cause issues with processing are filtered out.
    #Allowing unlikely names means you will probably have to modify your *.csv manually.
    class RegexType(str, Enum):
        STANDALONE = '.\p{Han}{2,4}.'
        COMBO = '.\p{Han}{2,4}.\p{Hiragana}+..'
        SUB_NAME = '\p{Han}{1,4}'
        HIRAGANA = '\p{Hiragana}+'

    def __init__(self, names = [], word_freq = [], allow_unlikely_names=False, standalone_name_regex=RegexType.STANDALONE, combo_name_regex=RegexType.COMBO, sub_name_regex=RegexType.SUB_NAME):
        self.allow_unlikely_names = allow_unlikely_names
        self.standalone_name_regex = standalone_name_regex
        self.combo_name_regex = combo_name_regex
        self.sub_name_regex = sub_name_regex
        self.names = names
        self.word_freq = word_freq
        self.names_sorted = []
    def process(self):
        if self.names:
            print("Initial set:")
            print(self.names)
            unknown_name = "Name With Unknown Reading"
            names_with_readings = {}
            for maybe_names in self.names:
                standalone_names = regex.findall(self.standalone_name_regex, maybe_names)
                for name in standalone_names:
                    name = regex.findall(self.sub_name_regex,name)[0]
                    if name not in names_with_readings.keys():
                        print("Found name: " + name)
                        names_with_readings[name] = None
                combo_names = regex.findall(self.combo_name_regex, maybe_names)

                for name in combo_names:
                    print("Searching for hiragana in: " + name)
                    names_kanji = regex.findall(self.sub_name_regex,name)
                    names_hiragana = regex.findall(self.RegexType.HIRAGANA,name)
                
        
                    if names_kanji[0] not in names_with_readings.keys() or names_with_readings[names_kanji[0]] is None or len(names_with_readings[names_kanji[0]]):
                        names_with_readings[names_kanji[0]] = names_hiragana[0]
   

            #Count the names
            names_count = {}
            for name in names_with_readings:
                try:
                    names_count[name] = self.word_freq[name]
                    #print("Appending frequency of " + name + " to list.")
                except:
                    #Could not find usage count, default to zero
                    names_count[name] = -1
                    self.word_freq[name] = -1
            
            for name in names_count:
                if self.word_freq[name] > 0 or self.allow_unlikely_names:
                    try:
                        #print("Appending " + name + " to list.")
                        self.names_sorted.append((name,names_with_readings[name],self.word_freq[name]))
                    except:
                        continue
            return True

    def regex_test(self, text, pattern):
        res = regex.findall(pattern, text)
        if res:
            return res
        else:
            return False