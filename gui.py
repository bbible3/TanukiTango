import json
import operator
import sys
import os
import time
import asyncio

from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QGridLayout, QTabWidget, QPushButton, QLineEdit, QProgressBar, QComboBox
from vproc import TanukiVproc
from ocr import TanukiOcr
from nlp import TanukiNlp
from subtitler import TanukiSubtitler

import config

exclusion_type = TanukiSubtitler.FilterType.INCLUDE_ALL
name_extraction = TanukiSubtitler.NameMode.NO_NAMES
my_starting_dir = os.path.dirname(os.path.realpath(__file__))

def loadDirectory(textbox):
    #Get the directory
    directory = QFileDialog.getOpenFileName(window, 'Select Directory', textbox.text(), filter="Mp4 Files (*.mp4)")
    print(directory)
    if len(directory[0])>0:
        QLineEdit.setText(textbox, directory[0])
def runExtraction(textbox, statusLabel=None):

    setTextTo = "Status: Extracting frames..."

    #Update the status label
    if statusLabel:
        statusLabel.setText(setTextTo)

    

    #Get the file
    directory = textbox.text()

    #Get just the name of the file without directories
    filename = directory.split(os.path.sep)[-1]
    #Replace the period with a dash
    filename_subdir = filename.replace(".", "-")
    #Get just the directory without the file
    working_directory = directory.replace(filename, "")

    our_subdir = working_directory + filename_subdir
    if not os.path.exists(our_subdir):
        os.makedirs(our_subdir)
        os.makedirs(our_subdir + "/frames")
    else:
        print("Directory already exists")
        
    #Force a refresh
    QApplication.processEvents()

    TanukiVproc.extractAllFrames(directory, our_subdir + "/frames/")
def runSeparation(textbox, statusLabel=None):
 

    

    #Get the file
    directory = textbox.text()

    #Get just the name of the file without directories
    filename = directory.split(os.path.sep)[-1]
    #Replace the period with a dash
    filename_subdir = filename.replace(".", "-")
    #Get just the directory without the file
    working_directory = directory.replace(filename, "")

    our_subdir = working_directory + filename_subdir
    if not os.path.exists(our_subdir):
        os.makedirs(our_subdir)
        os.makedirs(our_subdir + "/frames")
    else:
        print("Directory already exists")
        
    our_subdir = our_subdir + "/frames/"
    print("Running separation in:", our_subdir)
    setTextTo = "Status: Separating " + str(TanukiVproc.countFrames(our_subdir)) + " frames..."
    #Update the status label
    if statusLabel:
        statusLabel.setText(setTextTo)

    #Force a refresh
    QApplication.processEvents()

    TanukiVproc.processFrames(our_subdir)

def getOCRFolder(textbox, statusLabel=None):
    print("Getting OCR folder")
    directory = QFileDialog.getExistingDirectory(window, 'Select Directory', textbox.text())
    textbox.setText(directory)
    
def startOCR(textbox, statusLabel=None):
    print("Starting OCR")
    directory = textbox.text()
    setTextTo = "Status: OCRing " + str(TanukiVproc.countFrames(directory)) + " frames..."
    print(setTextTo)
    #Update the status label
    if statusLabel:
        statusLabel.setText(setTextTo)

    #Force a refresh
    QApplication.processEvents()

    TanukiOcr.processAll(directory, directory + "/txt/", ocrMode="none")
def removeSpaces(textbox, statusLabel=None):
    print("Removing spaces")
    directory = textbox.text()
    setTextTo = "Status: Removing spaces from " + str(TanukiVproc.countFrames(directory)) + " files..."
    #Update the status label
    if statusLabel:
        statusLabel.setText(setTextTo)

    #Force a refresh
    QApplication.processEvents()

    TanukiOcr.removeSpaces(directory + "/txt/")

def getNLPFolder(textbox, statusLabel=None):
    print("Getting NLP folder")
    directory = QFileDialog.getExistingDirectory(window, 'Select Directory', textbox.text())
    textbox.setText(directory)

def startNLP(textbox, statusLabel=None):
    print("Starting NLP")
    tnlp = TanukiNlp()
    directory = textbox.text()
    setTextTo = "Status: NLPing " + str(TanukiVproc.countFrames(directory)) + " files..."
    #Update the status label
    if statusLabel:
        statusLabel.setText(setTextTo)

    #Force a refresh
    QApplication.processEvents()

    print(directory)
    #Get a list of text files in the directory
    text_files = tnlp.getTextFiles(directory)

    for file in text_files:
        just_filename = file.split(os.path.sep)[-1]
        just_filename_no_ext = just_filename.split(".")[0]
        write_name = just_filename_no_ext + ".tnk"
        print("Writing to:", write_name)
        res = tnlp.annotateTextFile(file)
        tnlp.writeResult(write_name, res)

def getTNKFolder_async(textbox, statusLabel=None, outputLabel=None):
    dir_suc = getTNKFolder(textbox)
    if dir_suc:
        print("Got directory:", dir_suc)
        processTNKFolder(textbox, dir_suc, statusLabel, outputLabel)
    else:
        print("No directory selected")
    # #Update the status label when we have a directory
    # if statusLabel:
    #     statusLabel.setText("Status: Loading " + dir_suc)
    # if len(dir_suc)>0:
    #     processTNKFolder(textbox, dir_suc, statusLabel)

def getTNKFolder(textbox, statusLabel=None):
    print("Getting NLP folder")
    #directory = QFileDialog.getExistingDirectory(window, 'Select Directory', textbox.text())
    directory = QFileDialog(window)
    result = directory.getExistingDirectory()
    if result:
        print("Got directory:", result)
        directory = result
    else:
        print("No directory selected")
        directory = ""
    return directory

def processTNKFolder(textbox, directory, statusLabel=None, outputLabel=None):
    print("Processing TNK folder")
    textbox.setText(directory)
    #Get a list of the *.tnk files in the directory
    tnlp = TanukiNlp()
    tnk_files = tnlp.getTNKFiles(directory)
    how_many = len(tnk_files) if True else 0
    setTextTo = "Status: Found " + str(how_many) + " *.tnk files"
    #Update the status label
    if statusLabel:
        statusLabel.setText(setTextTo)
    
    #Force a refresh
    QApplication.processEvents()

    rvals = tnlp.processTNKFiles(tnk_files, statusLabel)
    result_str = ""
    
    counts = {}
    values = {}
    freq = {}
    for rval in rvals:
        for key in rval.keys():
            print("Key:", key)
            if key == "verb":
                continue
            if key not in counts:
                counts[key] = 0
                values[key] = []
            for val in rval[key]:
                counts[key] += 1
                if key == "lemmaPair":
                    values[key].append(val[1])
                else:
                    values[key].append(val)
    
    for key in counts.keys():
        for val in values[key]:
            if val not in freq:
                freq[val] = 0
            freq[val] += 1

    print("Counts:", counts)
    print("Sums to:", sum(counts.values()))
    print("Freq Sums to:", len(freq.keys()))
    dups = sum(counts.values()) - len(freq.keys())
    print("We can infer that the number of duplicates is:", dups)

    #Sort freq by value
    freq_sorted = sorted(freq.items(), key=operator.itemgetter(1), reverse=True)
    #Print the top 10
    for i in range(10):
        print(freq_sorted[i])
        result_str += str(freq_sorted[i]) + "\n"
    outputLabel.setText(result_str)
    outputLabel.repaint()

def getSubtitleFolder_async(textbox, statusLabel=None, outputLabel=None):
    dir_suc = getSubtitleFolder(textbox)
    if dir_suc:
        print("Got directory:", dir_suc)
        processSubtitleFolder(textbox, dir_suc, statusLabel, outputLabel)
    else:
        print("No directory selected")
    # #Update the status label when we have a directory
    # if statusLabel:
    #     statusLabel.setText("Status: Loading " + dir_suc)
    # if len(dir_suc)>0:
    #     processTNKFolder(textbox, dir_suc, statusLabel)
    #Has my cwd changed from when I started?

def getSubtitleFolder(textbox, statusLabel=None):
    print("Getting Subtitle folder")
    #directory = QFileDialog.getExistingDirectory(window, 'Select Directory', textbox.text())
    directory = QFileDialog(window)
    result = directory.getExistingDirectory()
    if result:
        print("Got directory:", result)
        directory = result
    else:
        print("No directory selected")
        directory = ""
    return directory
def processSubtitleFolder(textbox, directory, statusLabel=None, outputLabel=None):
    textbox.setText(directory)
    print("Processing Subtitle folder")
    outputLabel.setText("Subtitle folder loaded.")

def updateExclusionType(tab_5_exclusion_dropndown):
    exclusion_type = tab_5_exclusion_dropndown.currentText()
    if exclusion_type == "Don\'t Filter":
        exclusion_type = TanukiSubtitler.FilterType.INCLUDE_ALL
    elif exclusion_type == "Only Include Genki Words":
        exclusion_type = TanukiSubtitler.FilterType.INCLUDE_ONLY_GENKI
    elif exclusion_type == "Exclude Genki Words":
        exclusion_type = TanukiSubtitler.FilterType.EXCLUDE_GENKI
    print("Exclusion type:", exclusion_type)

def updateNameExtraction(tab_5_name_dropdown):
    name_extraction = tab_5_name_dropdown.currentText()
    if name_extraction == "Don\'t Extract Names":
        name_extraction = TanukiSubtitler.NameMode.NO_NAMES
    elif name_extraction == "Extract Names":
        name_extraction = TanukiSubtitler.NameMode.NAMES
    elif name_extraction == "Loose Extract Names":
        name_extraction = TanukiSubtitler.NameMode.NAMES_STRONG
    print("Name extraction:", name_extraction)
    return name_extraction


def startSubtitleExtraction_async(tab_5_input_textbox, statusLabel=None, outputLabel=None, nameModeDropdown=None):
    if my_starting_dir is not os.path.dirname(os.path.realpath(__file__)):
        print("My cwd has changed!")
        os.chdir(my_starting_dir)
    dir = tab_5_input_textbox.text()
    if len(dir)>0:
        startSubtitleExtraction(tab_5_input_textbox, statusLabel, outputLabel, nameModeDropdown=nameModeDropdown)

def startSubtitleExtraction(tab_5_input_textbox, statusLabel=None, outputLabel=None, nameModeDropdown=None):
    subs = TanukiSubtitler(subtitle_files=tab_5_input_textbox.text(), exclusion_type=exclusion_type, name_mode=updateNameExtraction(nameModeDropdown))

def getTesseractFolder(textbox, statusLabel=None):
    print("Getting Executable")
    #directory = QFileDialog.getExistingDirectory(window, 'Select Directory', textbox.text())
    directory = QFileDialog(window)
    #Get .exe file
    result = directory.getOpenFileName(filter="Executable Files (*.exe)")
    if result:
        print("Got directory:", result)
        directory = result[0]
        return directory
    else:
        print("No directory selected")
        directory = ""

def processTesseractFolder(textbox, directory, config, statusLabel=None):
    #Update the status label when we have a directory
    config.tesseract_executable = directory
    config.saveConfig()
    return True

def getTesseractFolder_async(textbox, config, statusLabel=None):
    dir_suc = getTesseractFolder(textbox)
    if dir_suc:
        print("Got directory:", dir_suc)
        processTesseractFolder(textbox, dir_suc, config, statusLabel)
        textbox.setText(dir_suc)
    else:
        print("No directory selected")


app = QApplication([])

window = QWidget()
window.setWindowTitle('TanukiTango')
#window.setGeometry(100, 100, 300, 300)
#Set the window's minimum size
window.setMinimumSize(600, 300)

#Create a QHBoxLayout
layout = QGridLayout()
window.setLayout(layout)

#Generate content for the tabs


myConfig =config.TanukiTangoConfig()

#Tab 1
tab1 = QWidget()
tab1_layout = QGridLayout()
tab1.setLayout(tab1_layout)
tab1_label1 = QLabel('<h1>Frame Extraction</h1>')
tab1_label2 = QLabel('<h2>Select an MP4 video file to extract unique frames.</h2>')

tab1_tabtext = "Frame Extraction"

#A textbox and button to select the video file
tab1_textbox = QLineEdit('')
tab1_textbox_default = TanukiVproc.curDir()
tab1_textbox.setText(tab1_textbox_default)

tab1_textbox.setReadOnly(True)
tab1_button = QPushButton('Select Video File')
tab1_button.clicked.connect(lambda: loadDirectory(tab1_textbox))

tab1_start_button = QPushButton('Begin frame extraction')
tab1_start_button.clicked.connect(lambda: runExtraction(tab1_textbox, statusLabel=tab1_status_label))

tab1_status_label = QLabel('Status: Waiting...')

tab1_start_proc = QPushButton('Begin frame separation')
tab1_start_proc.clicked.connect(lambda: runSeparation(tab1_textbox, statusLabel=tab1_status_label))

#Add labels
#Add tab1_label1 to the layout
tab1_layout.addWidget(tab1_label1, 0, 0)
#Add tab1_label2 to the layout
tab1_layout.addWidget(tab1_label2, 1, 0)
#Add tab1_textbox to the layout
tab1_layout.addWidget(tab1_textbox, 2, 0)
#Add tab1_button to the layout
tab1_layout.addWidget(tab1_button, 2, 1)
#Add tab1_start_button to the layout
tab1_layout.addWidget(tab1_start_button, 3, 0)
#Add tab1_status_label to the layout
tab1_layout.addWidget(tab1_status_label, 4, 0)
#Add tab1_start_proc to the layout
tab1_layout.addWidget(tab1_start_proc, 5, 0)

#Tab 2
tab2 = QWidget()
tab2_layout = QGridLayout()
tab2.setLayout(tab2_layout)

tab2_label = QLabel('<h1>Auto OCR</h1>')
tab2_tabtext = "Auto OCR"
tab2_label2 = QLabel('<h2>Select a folder of frames to attempt OCR on.</h2>')

#Text box and button to select the video file
tab2_textbox = QLineEdit('')
tab2_textbox_default = TanukiVproc.curDir()
#Make it read only
tab2_textbox.setReadOnly(True)
tab2_textbox.setText(tab2_textbox_default)

tab2_button = QPushButton('Select Folder')
tab2_button.clicked.connect(lambda: getOCRFolder(tab2_textbox, statusLabel=tab2_status_label))
tab2_status_label = QLabel('Status: Waiting...')
tab2_start_ocr_button = QPushButton('Begin OCR')
tab2_start_ocr_button.clicked.connect(lambda: startOCR(tab2_textbox, statusLabel=tab2_status_label))

tab2_remove_spaces_button = QPushButton('Remove Spaces')
tab2_remove_spaces_button.clicked.connect(lambda: removeSpaces(tab2_textbox, statusLabel=tab2_status_label))



#Add label to the layout
tab2_layout.addWidget(tab2_label, 0, 0)
#Add label2 to the layout
tab2_layout.addWidget(tab2_label2, 1, 0)
#Add textbox to the layout
tab2_layout.addWidget(tab2_textbox, 2, 0)
#Add button to the layout
tab2_layout.addWidget(tab2_button, 2, 1)
#Add status label to the layout
tab2_layout.addWidget(tab2_status_label, 3, 0)
#Add start button to the layout
tab2_layout.addWidget(tab2_start_ocr_button, 4, 0)
#Add remove spaces button to the layout
tab2_layout.addWidget(tab2_remove_spaces_button, 5, 0)


#Tab 3
tab3 = QWidget()
tab3_layout = QGridLayout()
tab3.setLayout(tab3_layout)
tab3_label = QLabel('<h1>Language Processing</h1>')
tab3_label2 = QLabel('<h2>Process extracted vocab</h2>')
tab3_tabtext = "Language Processing"

#Add the label to the layout
tab3_layout.addWidget(tab3_label, 0, 0)
#Add the label2 to the layout
tab3_layout.addWidget(tab3_label2, 1, 0)

tab3_textbox = QLineEdit('')
tab3_button = QPushButton('Select Folder')
tab3_button.clicked.connect(lambda: getNLPFolder(tab3_textbox, statusLabel=tab3_status_label))
tab3_status_label = QLabel('Status: Waiting...')
tab3_start_nlp_button = QPushButton('Process folder...')
tab3_start_nlp_button.clicked.connect(lambda: startNLP(tab3_textbox, statusLabel=tab3_status_label))

tab3_layout.addWidget(tab3_textbox, 2, 0)
tab3_layout.addWidget(tab3_button, 2, 1)
tab3_layout.addWidget(tab3_status_label, 3, 0)
tab3_layout.addWidget(tab3_start_nlp_button, 4, 0)

#Tab 4
tab4 = QWidget()
tab4_layout = QGridLayout()
tab4.setLayout(tab4_layout)
tab4_label = QLabel('<h1>*.tnk explorer</h1>')
tab4_label2 = QLabel('<h2>Load processed vocabulary files</h2>')
tab4_tabtext = "*.tnk Explorer"

tab4_textbox = QLineEdit('')
tab4_button = QPushButton('Select Folder')
tab4_button.clicked.connect(lambda: getTNKFolder_async(tab4_textbox, statusLabel=tab4_status_label, outputLabel=tab4_results_label))
tab4_status_label = QLabel('Status: Waiting...')
tab4_results_label = QLabel('')
#Add the label to the layout
tab4_layout.addWidget(tab4_label, 0, 0)
#Add the label2 to the layout
tab4_layout.addWidget(tab4_label2, 1, 0)
#Add the textbox to the layout
tab4_layout.addWidget(tab4_textbox, 2, 0)
#Add the button to the layout
tab4_layout.addWidget(tab4_button, 2, 1)
#Add the status label to the layout
tab4_layout.addWidget(tab4_status_label, 3, 0)
tab4_layout.addWidget(tab4_results_label, 4, 0)

#Tab 5
tab_5 = QWidget()
tab_5_layout = QGridLayout()
tab_5.setLayout(tab_5_layout)
tab_5_label = QLabel('<h1>Subtitle Extractor</h1>')
tab_5_label2 = QLabel('<h2>Extract vocabulary from *.srt subtitle files</h2>')
tab_5_tabtext = "Subtitle Extractor"
tab_5_status_label = QLabel('Status: Waiting...')
tab_5_results_label = QLabel('')
#The textbox and button to select the folder
tab_5_textbox = QLineEdit('')
tab_5_button = QPushButton('Select Folder')

#A dropdown to select exclusion type
tab_5_exclusion_dropdown_label = QLabel('Exclusion Type:')
tab_5_exclusion_dropdown = QComboBox()
tab_5_exclusion_dropdown.addItems(['Don\'t Filter', 'Only Include Genki Words', 'Exclude Genki Words'])
tab_5_exclusion_dropdown.currentIndexChanged.connect(lambda: updateExclusionType(tab_5_exclusion_dropdown))

#A dropdown to select name extraction
tab_5_name_dropdown_label = QLabel('Name Extraction:')
tab_5_name_dropdown = QComboBox()
tab_5_name_dropdown.addItems(['Don\'t Extract Names', 'Extract Names', 'Loose Extract Names'])
tab_5_name_dropdown.currentIndexChanged.connect(lambda: updateNameExtraction(tab_5_name_dropdown))

tab_5_button.clicked.connect(lambda: getSubtitleFolder_async(tab_5_textbox, statusLabel=tab_5_status_label, outputLabel=tab_5_results_label))

#A button to start the extraction
tab_5_start_button = QPushButton('Start Extraction')
tab_5_start_button.clicked.connect(lambda: startSubtitleExtraction_async(tab_5_textbox, statusLabel=tab_5_status_label, outputLabel=tab_5_results_label, nameModeDropdown=tab_5_name_dropdown))

tab_5_layout.addWidget(tab_5_label, 0, 0)
tab_5_layout.addWidget(tab_5_label2, 1, 0)
tab_5_layout.addWidget(tab_5_textbox, 2, 0)
tab_5_layout.addWidget(tab_5_button, 2, 1)
tab_5_layout.addWidget(tab_5_status_label, 3, 0)
tab_5_layout.addWidget(tab_5_results_label, 4, 0)
tab_5_layout.addWidget(tab_5_exclusion_dropdown_label, 5, 0)
tab_5_layout.addWidget(tab_5_exclusion_dropdown, 5, 1)
tab_5_layout.addWidget(tab_5_name_dropdown_label, 6, 0)
tab_5_layout.addWidget(tab_5_name_dropdown, 6, 1)
tab_5_layout.addWidget(tab_5_start_button, 7, 0)


#Tab 6: Config
tab_6 = QWidget()
tab_6_layout = QGridLayout()
tab_6.setLayout(tab_6_layout)
tab_6_label = QLabel('<h1>Config</h1>')
tab_6_label2 = QLabel('<h2>Configure TanukiTango</h2>')
tab_6_tabtext = "Config"
#"Tesseract Executable" selector label
tab_6_tesseract_label = QLabel('Tesseract Executable:')
#The textbox and button to select the folder
tab_6_tesseract_textbox = QLineEdit('')
tab_6_tesseract_textbox.setText(myConfig.tesseract_executable)
tab_6_tesseract_button = QPushButton('Select Folder')
tab_6_tesseract_button.clicked.connect(lambda: getTesseractFolder_async(tab_6_tesseract_textbox, myConfig, statusLabel=tab_6_status_label))
tab_6_status_label = QLabel('Status: Not selected...')
if myConfig.tesseract_executable:
    tab_6_status_label.setText("Status: " + myConfig.tesseract_executable)

#Dropdown to select language_mode: either jpn or jpn_vert
tab_6_language_mode_label = QLabel('Language Mode:')
tab_6_language_mode_dropdown = QComboBox()
tab_6_language_mode_dropdown.addItems(['Not set', 'jpn', 'jpn_vert'])
tab_6_language_mode_dropdown.currentIndexChanged.connect(lambda: myConfig.setLanguageMode(tab_6_language_mode_dropdown.currentText()))
if myConfig.language_mode:
    tab_6_language_mode_dropdown.setCurrentText(myConfig.language_mode)

#Add label to guide user to install languagepacks into ./tessdata from https://github.com/tesseract-ocr/tessdata/
tab_6_languagepacks_label = QLabel('<h3>Install languagepacks into ./tessdata from <a href="https://github.com/tesseract-ocr/tessdata/">Github</a></h3>')
#Add label for https://github.com/tesseract-ocr/tessdoc/blob/main/tess3/Data-Files.md
#tab_6_languagepacks_label = QLabel('<h3>Install languagepacks into ./tessdata from <a href="https://github.com/tesseract-ocr/tessdoc/blob/main/tess3/Data-Files.md">Github</a></h3>')
tab_6_languagepacks_label.setOpenExternalLinks(True)
#Add label to guide about environment variables
tab_6_env_var_label = QLabel('<h3>Set environment variables:</h3><br/><h4>Ensure you have added TESSDATA_PREFIX to point to Tesseract-OCR\\tessdata and added Tesseract-OCR\\ to your System PATH</h4>')


tab_6_layout.addWidget(tab_6_label, 0, 0)
tab_6_layout.addWidget(tab_6_label2, 1, 0)
tab_6_layout.addWidget(tab_6_tesseract_label, 2, 0)
tab_6_layout.addWidget(tab_6_tesseract_textbox, 2, 1)
tab_6_layout.addWidget(tab_6_tesseract_button, 2, 2)
tab_6_layout.addWidget(tab_6_status_label, 3, 0)
tab_6_layout.addWidget(tab_6_language_mode_label, 4, 0)
tab_6_layout.addWidget(tab_6_language_mode_dropdown, 4, 1)
tab_6_layout.addWidget(tab_6_languagepacks_label, 5, 0)


#Add the tabs
tabwidget = QTabWidget()
tabwidget.addTab(tab1, tab1_tabtext)
tabwidget.addTab(tab2, tab2_tabtext)
tabwidget.addTab(tab3, tab3_tabtext)
tabwidget.addTab(tab4, tab4_tabtext)
tabwidget.addTab(tab_5, tab_5_tabtext)
tabwidget.addTab(tab_6, tab_6_tabtext)

layout.addWidget(tabwidget, 0,0)

#A file select dialog
#fileName = QFileDialog.getOpenFileName(window, 'Open file', '/home')
#print(fileName[0])

window.show()
sys.exit(app.exec())

