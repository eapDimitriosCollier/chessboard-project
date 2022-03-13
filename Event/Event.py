from threading import Lock



class Event():
    """Thread safe Event"""
    __eventList = {}
    
    def __init__(self, eventName, **eventKwargs):
        self.__currEvent = None
        
        if eventName not in Event.__eventList:
            self.__currEvent = self.createNewEvent(eventName, **eventKwargs)
        else:
            self.__currEvent = Event.__eventList[eventName]
        
        for variableName, variableContents in eventKwargs.items():
            setattr(self.__currEvent, variableName, variableContents)    
    
    def __getattr__(self, eventFuncName):
        return getattr(self.__currEvent, eventFuncName)
       
    def createNewEvent(self, EventName, **eventKwargs):
        eventCls = type(EventName, (), {
            'subscribe' : subscribe,
            'unsubscribe' : unsubscribe,
            'invoke' : invoke
        })
        
        setattr(eventCls, '__lock', Lock())
        setattr(eventCls, '__eventListeners', [])
        setattr(eventCls, '__eventName', EventName)
        
        for variableName, variableContents in eventKwargs.items():
            setattr(eventCls, variableName, variableContents)
            
        Event.__eventList[EventName] = eventCls
        return eventCls
            
@classmethod
def subscribe(event, eventListener):
    event.__lock.acquire()
    event.__eventListeners.append(eventListener)
    event.__lock.release()

@classmethod
def unsubscribe(event, eventListener):
    event.__lock.acquire()
    event.__eventListeners.remove(eventListener)
    event.__lock.release() 

@classmethod
def invoke(event):
    eventName =  event.__eventName
    
    event.__lock.acquire()
    for eventListener in event.__eventListeners:
        getattr(eventListener, f'on{eventName}')(event)
    event.__lock.release()       