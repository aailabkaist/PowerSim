class Event:

    def __init__(self,model,varOutput,varMessage,blnResolutionChange = False):
        self.modelSender = model
        self.portSender = varOutput
        self.message = varMessage
        self.blnResolutionChange = blnResolutionChange

    def getMessage(self):
        return self.message

    def getSenderModel(self):
        return self.modelSender

    def getSenderPort(self):
        return self.portSender

    def getResolutionChange(self):
        return self.blnResolutionChange

    def __eq__(self, other):
        if isinstance(other,Event) == True:
            if self.modelSender == other.getSenderModel():
                if self.portSender == other.getSenderPort():
                    if self.getMessage() == other.getMessage():
                        return True
        return False

    def __str__(self):
        return "Event : Sender : "+self.modelSender.getModelID()+", Port : "+self.portSender+", Resolution Change : "+str(self.blnResolutionChange)+", Message : "+str(self.message)

class ResolutionEvent(Event):
    def __init__(self,model,varMessage):
        super().__init__(model,'__ResolutionPort__',varMessage,blnResolutionChange = True)