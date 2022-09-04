import spacy
from spacy import displacy

nlp = spacy.load("ja_core_news_trf")
def annotateTextFile(filePath, ignoreStopWords=True, visualize=False):
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
    doc = nlp(text)
    nouns = []
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

    #Extract Entities
    for ent in doc.ents:
        entities[ent.text] = {"label": ent.label_, "start": ent.start_char, "end": ent.end_char}

    rval = {"nouns": nouns, "entities": entities, "verbs": verbs, "lemmaPairs": lemmaPairs}

    for key,val in rval.items():
        print(key + ": " + str(len(val)))
    
    if visualize:
        displacy.serve(doc, style=visualize)
    return rval

rval = annotateTextFile("txt/test.txt")

# for entity in rval["entities"]:
#     print("Named Entity:", entity)
#     #Print the entity's key and values
#     for key,val in rval["entities"][entity].items():
#         print(key + ": " + str(val))

for noun in rval["nouns"]:
    print("Noun:", noun)