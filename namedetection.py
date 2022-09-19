import regex
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

    def __init__(self, allow_unlikely_names=False, standalone_name_regex='.\p{Han}{2,4}.', combo_name_regex='.\p{Han}{2,4}.\p{Hiragana}+..'):
        self.allow_unlikely_names = allow_unlikely_names
        self.standalone_name_regex = standalone_name_regex
        self.combo_name_regex = combo_name_regex
        
