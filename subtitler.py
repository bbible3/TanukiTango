import glob
import os
import zipfile
import json
from sudachipy import tokenizer
from sudachipy import dictionary
import pysrt
import operator
import csv
from se import TanukiSubtitlerVals

class TanukiSubtitler:
    def __init__(self, genki_filename="res/genki-vocab.json", dictionary_filename="./res/jmdict_english.zip", subtitle_files="./subtitles", save_as="gen/Generated_Subtitles.csv", select_range=10, max_definitions=3, max_sub_defs=3):
        
        self.genki_filename = genki_filename
        try:
            self.genki_json = json.load(open(genki_filename, encoding="utf-8"))
        except Exception as e:
            print("Could not load genki json file", e)
            self.genki_json = {}
        self.dictionary_filename = dictionary_filename
        self.dict = self.load_dictionary(self.dictionary_filename)
        self.tokenizer_obj = dictionary.Dictionary(dict='small').create()
        self.mode = tokenizer.Tokenizer.SplitMode.A
        self.read_dir = True
        self.select_range = select_range
        self.max_definitions = max_definitions
        self.max_sub_defs = max_sub_defs
        self.save_as = save_as
        #is save_as the default?
        if save_as == "gen/Generated_Subtitles.csv":
            self.save_as = os.path.join(os.path.dirname(os.path.realpath(__file__)), save_as)

        # Is subtitle_files an array of strings or one string?
        if isinstance(subtitle_files, list):
            self.subtitle_files = subtitle_files
            self.read_dir = False
        else:
            self.subtitle_files = [subtitle_files]
            self.read_dir = True

        if self.read_dir:
            os.chdir(self.subtitle_files[0])
            for file in glob.glob("*.srt"):
                self.subtitle_files.append(file)

        else:
            # Does the subtitle_files list contain at least one entry?
            if len(self.subtitle_files) <= 0:
                raise Exception("No subtitle files given")
        if self.read_dir:
            print("Reading directory: " + self.subtitle_files[0])
            # Pop 0th element
            self.subtitle_files.pop(0)
        print(f"Subtitle files found: {len(self.subtitle_files)}")

        line_index = 0
        lines = []
        dlinect = 0
        ignored = 0
        maybe_names_preprocessing = []
        for filename in self.subtitle_files:
            with open(filename, encoding="utf8") as file:
                for line in file:
                    # Do our best to intelligently read the SRT
                    if line.isnumeric():
                        ignored += 1
                        continue
                    if line.count(":") >= 2 and line.count("-") > 1:
                        ignored += 1
                        continue
                    if len(line) <= 1:
                        ignored += 1
                        continue
                    if "(" in line and ")" in line:
                        print("Found possible name: " + line)
                        maybe_names_preprocessing.append(line)
                    dlinect += 1
                    lines.append(line.strip())
                    line_index += 1
        print(f"Lines read: {dlinect}")
        print(f"Ignored lines: {ignored}")

        # Begin tokenizing
        print("Tokenizing...")
        subs = pysrt.open(filename)
        tokenized_lines = []
        tokenized_lines_dic = []
        tokenized_types = {}
        tokenized_words = 0
        for line in subs:
            tokenized_line = [
                m.surface() for m in self.tokenizer_obj.tokenize(line.text, self.mode)]
            tokenized_line_dic = [
                m.dictionary_form() for m in self.tokenizer_obj.tokenize(line.text, self.mode)]
            tokenized_lines.append(tokenized_line)
            tokenized_lines_dic.append(tokenized_line_dic)
            tokenized_words += len(tokenized_line)
        print("Tokenized", len(subs), "lines into",
              tokenized_words, "tokenized elements")

        word_freq = {}
        for sentence in tokenized_lines_dic:
            for one_word in sentence:
                if one_word not in word_freq:
                    word_freq[one_word] = 0
                word_freq[one_word] += 1
        sorted_word_values = sorted(word_freq.values())
        sorted_words = sorted(word_freq)
        select_words = 10

        sorted_d = dict(sorted(word_freq.items(), key=operator.itemgetter(1), reverse=True))

        should_exclude = False
        exclude = []

        if should_exclude:
            exclude = TanukiSubtitlerVals.exclusions()

        verbs = []
        nouns = []
        adj = []
        adv = []
        for word in sorted_d:
            m = self.tokenizer_obj.tokenize(word, self.mode)[0]
            part = m.part_of_speech()[0]
            print(word, "Found a word of part:", part)
            if part == '動詞':
                verbs.append(word)
            if part == '名詞':
                nouns.append(word)
            if part == '形容詞' or part == '形動詞':
                adj.append(word)
            if part == '副詞':
                adv.append(word)
        print("Categorised into",len(verbs),"verbs,",len(nouns),"nouns,",len(adj),"adjectives and",len(adv),"adverbs")

        #Genki overlap section
        o_verbs = []
        o_nouns = []
        o_adj = []
        o_adv = []

        
        should_we_filter = True
        should_we_reverse_filter = True

        overlap_genki = should_we_filter

        genki_kanji = []
        for i in self.genki_json:
            genki_kanji.append(i['Kanji'])
            print(i['Kanji'])
        if overlap_genki:
            for item in verbs:
                if item in genki_kanji:
                    o_verbs.append(item)
            for item in nouns:
                if item in genki_kanji:
                    o_nouns.append(item)
            for item in adj:
                if item in genki_kanji:
                    o_adj.append(item)
            for item in adv:
                if item in genki_kanji:
                    o_adv.append(item)
        else:
            if should_we_reverse_filter:
                for item in verbs:
                    if item not in genki_kanji:
                        o_verbs.append(item)
                for item in nouns:
                    if item not in genki_kanji:
                        o_nouns.append(item)
                for item in adj:
                    if item not in genki_kanji:
                        o_adj.append(item)
                for item in adv:
                    if item not in genki_kanji:
                        o_adv.append(item)
            else:
                for item in verbs:
                    o_verbs.append(item)
                for item in nouns:
                    o_nouns.append(item)
                for item in adj:
                    o_adj.append(item)
                for item in adv:
                    o_adv.append(item)

        print("Genki overlap:",len(o_verbs),"verbs,",len(o_nouns),"nouns,",len(o_adj),"adjectives and",len(o_adv),"adverbs")

        o_verb_pairs = []
        o_noun_pairs = []
        o_adj_pairs = []
        o_adv_pairs = []

        for item in o_verbs:
            tup = (item, self.look_up(item))
            o_verb_pairs.append(tup)
        for item in o_nouns:
            tup = (item, self.look_up(item))
            o_noun_pairs.append(tup)
        for item in o_adj:
            tup = (item, self.look_up(item))
            o_adj_pairs.append(tup)
        for item in o_adv:
            tup = (item, self.look_up(item))
            o_adv_pairs.append(tup)

        print("Generated pairs...")
        print("Showing up to", select_range, "words of each type of vocab")

        #Verbs
        v_tup = []
        for i in range(0,min(len(o_verb_pairs), self.select_range)):
            this_verb_pair = o_verb_pairs[i]
            this_verb = this_verb_pair[0]
            this_info = this_verb_pair[1]
            if this_verb_pair is None or this_verb is None or this_info is None:
                continue
            tup2 = "Common reading: " + this_info[0]['reading'] + "<br/>" + "Appears " + str(word_freq[this_verb]) + " times" + "<br/>" + "Word has " + str(len(this_info)) + " distinct definitions"
            for j in range(0,min(len(this_info),max_definitions)):
                tup2 += "<br/>"
                tup2 += this_info[j]['reading']
                sub_gloss = this_info[j]['glossary_list']
                sub_gloss_str = ""
                for q in sub_gloss:
                    sub_gloss_str += q + ", "
                tup2 += "<br/>" + sub_gloss_str
            this_tup = (this_verb, tup2, this_info[0]['reading'], this_info[0]['glossary_list'][0])
            v_tup.append(this_tup)
        
        #Nouns
        n_tup = []
        for i in range(0,min(len(o_noun_pairs), self.select_range)):
            this_noun_pair = o_noun_pairs[i]
            this_noun = this_noun_pair[0]
            this_info = this_noun_pair[1]
            if this_noun_pair is None or this_noun is None or this_info is None:
                continue
            tup2 = "Common reading: " + this_info[0]['reading'] + "<br/>" + "Appears " + str(word_freq[this_noun]) + " times" + "<br/>" + "Word has " + str(len(this_info)) + " distinct definitions"
            for j in range(0,min(len(this_info),max_definitions)):
                tup2 += "<br/>"
                tup2 += this_info[j]['reading']
                sub_gloss = this_info[j]['glossary_list']
                sub_gloss_str = ""
                for q in sub_gloss:
                    sub_gloss_str += q + ", "
                tup2 += "<br/>" + sub_gloss_str
            this_tup = (this_noun, tup2, this_info[0]['reading'], this_info[0]['glossary_list'][0])
            n_tup.append(this_tup)
        j_tup = []
        
        #Adjectives
        for i in range(0,min(len(o_adj_pairs), self.select_range)):
            this_adj_pair = o_adj_pairs[i]
            this_adj = this_adj_pair[0]
            this_info = this_adj_pair[1]
            if this_adj_pair is None or this_adj is None or this_info is None:
                continue
            tup2 = "Common reading: " + this_info[0]['reading'] + "<br/>" + "Appears " + str(word_freq[this_adj]) + " times" + "<br/>" + "Word has " + str(len(this_info)) + " distinct definitions"
            for j in range(0,min(len(this_info),max_definitions)):
                tup2 += "<br/>"
                tup2 += this_info[j]['reading']
                sub_gloss = this_info[j]['glossary_list']
                sub_gloss_str = ""
                for q in sub_gloss:
                    sub_gloss_str += q + ", "
                tup2 += "<br/>" + sub_gloss_str
            this_tup = (this_adj, tup2, this_info[0]['reading'], this_info[0]['glossary_list'][0])
            j_tup.append(this_tup)

        #Adverbs
        b_tup = []
        for i in range(0,min(len(o_adv_pairs), self.select_range)):
            this_adv_pair = o_adv_pairs[i]
            this_adv = this_adv_pair[0]
            this_info = this_adv_pair[1]
            if this_adv_pair is None or this_adv is None or this_info is None:
                continue
            tup2 = "Common reading: " + this_info[0]['reading'] + "<br/>" + "Appears " + str(word_freq[this_adv]) + " times" + "<br/>" + "Word has " + str(len(this_info)) + " distinct definitions"
            for j in range(0,min(len(this_info),max_definitions)):
                tup2 += "<br/>"
                tup2 += this_info[j]['reading']
                sub_gloss = this_info[j]['glossary_list']
                sub_gloss_str = ""
                for q in sub_gloss:
                    sub_gloss_str += q + ", "
                tup2 += "<br/>" + sub_gloss_str
            this_tup = (this_adv, tup2, this_info[0]['reading'], this_info[0]['glossary_list'][0])
            b_tup.append(this_tup)
        rows = []
        for item in v_tup:
            rows.append([item[0], "Verb -- " + item[1]])
        for item in n_tup:
            rows.append([item[0], "Noun -- " + item[1]])
        for item in j_tup:
            rows.append([item[0], "Adjective -- " + item[1]])
        for item in b_tup:
            rows.append([item[0], "Adverb -- " + item[1]])
        with open(self.save_as, 'w+', encoding='utf8') as gs:
            writer = csv.writer(gs)
            writer.writerows(rows)
            print("Saved to " + self.save_as)

    def flip_dic_list(wd):
        temp = []
        for i in reversed(range(0,len(wd))):
            temp.append(wd[i])
        return temp

    def load_dictionary(self,dictionary):
        print("Loading dictionary...", dictionary)
        output_map = {}
        archive = zipfile.ZipFile(dictionary, 'r')
        result = list()
        for file in archive.namelist():
            if file.startswith('term'):
                with archive.open(file) as f:
                    data = f.read()
                    d = json.loads(data.decode("utf-8"))
                    result.extend(d)
        for entry in result:
            if (entry[0] in output_map):
                output_map[entry[0]].append(entry)
            else:
                output_map[entry[0]] = [entry]
        print("Loaded dictionary")
        return output_map

    def look_up(self, word):
        word = word.strip()
        if word not in self.dict:
            m = self.tokenizer_obj.tokenize(word, self.mode)[0]
            word = m.dictionary_form()
            if word not in self.dict:
                return None
        else:
            result = [{
            'headword': entry[0],
            'reading': entry[1],
            'tags': entry[2],
            'glossary_list': entry[5],
            'sequence': entry[6]
            } for entry in self.dict[word]]
            return result

#Cwd:

tester = TanukiSubtitler(subtitle_files="./subtitles/kanokari/")