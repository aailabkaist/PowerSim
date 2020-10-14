
class Logger:

    GENERAL = 0
    STATE = 1
    MESSAGE = 2
    TA = 3
    STRUCTURE = 4

    def __init__(self,engine,strFileName,blnLogGeneral,blnLogState,blnLogMessage,blnLogTA,blnLogStructure):
        self.engine = engine
        self.strFileName = strFileName
        if strFileName == -1:
            self.blnLogFile = False
        else:
            self.file = open(strFileName,'w')
            self.blnLogFile = True
        self.blnLogGeneral = blnLogGeneral
        self.blnLogState = blnLogState
        self.blnLogMessage = blnLogMessage
        self.blnLogTA = blnLogTA
        self.blnLogStructure = blnLogStructure

    def log(self,type,message):
        if type == Logger.STRUCTURE:
            if self.blnLogStructure == True:
                self.printOut("Structure Log", message)
        if type == Logger.GENERAL:
            if self.blnLogGeneral == True:
                self.printOut("General Log", message)
        if type == Logger.STATE:
            if self.blnLogState == True:
                self.printOut("State Log",message)
        if type == Logger.MESSAGE:
            if self.blnLogMessage == True:
                self.printOut("Message Log", message)
        if type == Logger.TA:
            if self.blnLogTA == True:
                self.printOut("TA Log", message)

    def printOut(self,strType,message):
        out = str(self.engine.getTime()) + "," + strType + "," + message
        if self.blnLogFile == True:
            self.file.write(out+"\n")
            self.file.flush()
        else:
            print(out)

    def __del__(self):
        self.file.close()
