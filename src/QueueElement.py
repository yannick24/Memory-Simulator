'''
Created on Sep 26, 2011

@author: yannick
'''

class MyElt():
    '''
    class used to reference item in my Custom Queue
    '''


    def __init__(self, itemNumber = '', size = 0, duration = 0, timeInQueue = 0, nextItem = None, prevItem = None):
        '''
        Constructor
        '''
        self.itemNumber = itemNumber
        self.size = size
        self.duration = duration
        self.timeInQueue = timeInQueue
        self.nextItem = nextItem
        self.prevItem = prevItem