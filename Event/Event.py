from threading import Lock



class Event():
    """Thread safe Event"""
    _eventList = {}
    
    def __init__(self, EventName, **EventKwargs):
        self._currEvent = None
        
        if EventName not in Event._eventList:
            self.createNewEvent(EventName, **EventKwargs)
        else:
            self._currEvent = Event._eventList[EventName]
    
    def __getattr__(self, eventFuncName):
        return getattr(self._currEvent, eventFuncName)
       
    def createNewEvent(self, EventName, **EventKwargs):
        eventCls = type(EventName, (), {
            'subscribe' : subscribe,
            'unsubscribe' : unsubscribe,
            'invoke' : invoke
        })
        
        setattr(eventCls, '__lock', Lock())
        setattr(eventCls, '__eventListeners', [])
        setattr(eventCls, '__eventName', EventName)
        for variableName, variableContents in EventKwargs.items():
            setattr(eventCls, variableName, variableContents)
        
        self._currEvent = eventCls()    
        Event._eventList[EventName] = self._currEvent     
            
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