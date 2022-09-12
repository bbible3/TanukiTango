import os
import spacy
import json
from spacy import displacy
class TanukiNlp:
    nlp = []
    def __init__(self):
        self.nlp = spacy.load("ja_core_news_trf")
    def annotateTextFile(self, filePath, ignoreStopWords=True, visualize=False):
        print("Loaded file for annotation: " + filePath)
        if ignoreStopWords:
            print("Ignoring stop words")
        
        #How many lines in the file?
        with open(filePath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        print("Number of lines: " + str(len(lines)))
        
        #Load the text file and save it to a string
        text = ""
        with open(filePath, "r", encoding='utf-8') as f:
            text = f.read()
        
        #Special pipes
        #nlp.add_pipe("merge_subtokens")
        #nlp.add_pipe("merge_entities")
        #nlp.add_pipe("merge_noun_chunks")
        #Create a Doc object from the text
        doc = self.nlp(text)
        nouns = []
        propns = []
        entities = {}
        verbs = []
        lemmaPairs = {}

        #Extract Word Parts
        for token in doc:
            if token.pos_ == "NOUN":
                if ignoreStopWords and token.is_stop:
                    continue
                nouns.append(token.text)
            elif token.pos_ == "VERB":
                verbs.append(token.text)
                lemmaPairs[token.text] = token.lemma_
            elif token.pos_ == "PROPN":
                propns.append(token.text)

        #Extract Entities
        for ent in doc.ents:
            entities[ent.text] = {"label": ent.label_, "start": ent.start_char, "end": ent.end_char}

        rval = {"nouns": nouns, "entities": entities, "verbs": verbs, "lemmaPairs": lemmaPairs, "propns": propns}

        for key,val in rval.items():
            print(key + ": " + str(len(val)))
        
        if visualize:
            displacy.serve(doc, style=visualize)
        return rval

    #rval = annotateTextFile("video/demo-mp4/frames/txt/146.txt")

    # for entity in rval["entities"]:
    #     print("Named Entity:", entity)
    #     #Print the entity's key and values
    #     for key,val in rval["entities"][entity].items():
    #         print(key + ": " + str(val))

    # for noun in rval["nouns"]:
    #     print("Noun:", noun)

    # for lemmaPair in rval["lemmaPairs"]:
    #     print("Lemma Pair:", lemmaPair)
    #     print("Lemma:", rval["lemmaPairs"][lemmaPair])

    #for propn in rval["propns"]:
    #    print("Propn:", propn)
    def writeResult(self, path, rval):
        print("Constructing JSON")
        #Construct the JSON
        jsonDict = {}
        jsonDict["nouns"] = rval["nouns"]
        jsonDict["entities"] = rval["entities"]
        jsonDict["verbs"] = rval["verbs"]
        jsonDict["lemmaPairs"] = rval["lemmaPairs"]
        jsonDict["propns"] = rval["propns"]
        print("Saving JSON")
        #Save the JSON
        with open(path, "w", encoding="utf-8") as f:
            json.dump(jsonDict, f, ensure_ascii=False)

    def readResult(self, path):
        print("Reading JSON")
        #Load the JSON
        with open(path, "r", encoding="utf-8") as f:
            json = f.read()
        #Convert to dict
        rval = eval(json)
        return rval

    def getTextFiles(self, path):
        txt_files = []
        for file in os.listdir(path):
            if file.endswith(".txt"):
                txt_files.append(path + "/" + file)
        return txt_files
    def getTNKFiles(self, path):
        tnk_files = []
        for file in os.listdir(path):
            if file.endswith(".tnk"):
                tnk_files.append(path + "/" + file)
        return tnk_files
    def processTNKFiles(self, tnk_files, statusLabel = None):
        rvals = []
        files_count = len(tnk_files)
        i = 0
        for file in tnk_files:
            i += 1
            if statusLabel != None:
                statusLabel.setText("Reading " + str(i) + " of " + str(files_count))
                #Force the status label to update
                statusLabel.repaint()
                
            print("Reading file: " + file)
            rval = self.readResult(file)
            #Append to rvals
            rvals.append(rval)
        return rvals