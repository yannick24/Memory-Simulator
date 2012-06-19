'''
Created on Sep 26, 2011

@author: yannick
'''

class MyPartition():
    '''
    class used to create partition in my memory simulator
    '''


    def __init__(self, name, size, duration = 0, status = None, space = None):
        '''
        Constructor
        '''
        self.name = name
        self.size = size
        self.duration = duration
        self.status = status
        self.nextPartition = None
        self.prevPartition = None
        self.space = space