'''
Created on Sep 26, 2011

@author: yannick
'''
from QueueElement import MyElt

class MyQueue():
    '''
    class for my custom Queue
    '''

    def __init__(self, length = 0, front = None, rear = None):
        '''
        Constructor
        '''
        self.length = length
        self.front = front
        self.rear = rear
    
    '''
    method to enqueue item (QueueElement) in Queue
    '''
    def enqueue(self, number, size, duration):
        # case : if Queue is empty, enter first element
        if (self.isEmpty()):
            node = MyElt(number, size, duration)
            self.front = node
            self.rear = node
            self.length = self.length + 1
            return
        # case :  if Queue is not empty, enter item at the end of the Queue
        node = self.rear
        last = MyElt(number, size, duration)
        last.prevItem = node
        node.nextItem = last
        if (self.front.itemNumber == node.itemNumber):
            self.front = node
        self.rear = last
        self.length = self.length + 1
        
    '''
    method used to dequeue first item in Queue
    '''
    def dequeue(self):
        # case : if Queue is empty, return nothing (None)
        if (self.isEmpty()):
            # print "MyQueue is Empty"
            return self.front
        # case :  if Queue has one item only
        if (self.length == 1):
            node = self.front
            self.front = None
            self.rear = None
            self.length = self.length - 1
            return node
        # case : if Queue has more than one item
        if (self.length > 1):
            node = self.front
            self.front = None
            self.front = node.nextItem
            self.front.prevItem = None
            self.length = self.length - 1
            return node
    
    '''
    Check if Queue is empty, return True if it is, false otherwise
    '''
    def isEmpty(self):
        return (self.length == 0)
    
    '''
    return first item in queue without removing it
    '''
    def frontElt(self):
        return self.front
    
    '''
    remove evrything in Queue
    '''
    def clear(self):
        if (self.isEmpty()):
            print "MyQueue is Empty"
            return
        while(self.front != None): 
            self.dequeue()
        print "\n" + "MyQueue length is " , self.length, "\n\n"
    
    '''
    print item(s) in Queue
    '''
    def printQueue(self):
        if (self.isEmpty()):
            print "MyQueue is Empty"
            return
        node = self.front
        while(node != None):
            print node.itemNumber, "\t", node.size, "\t", node.duration, "fortnights"
            node = node.nextItem
        print "\n" + "MyQueue length is " , self.length, "\n\n"
        
        
if __name__ == '__main__':
    memoryQueue = MyQueue()
    memoryQueue.enqueue(1, 6100, 12)
    memoryQueue.enqueue(2, 123, 2)
    memoryQueue.enqueue(3, 746, 32)
    memoryQueue.enqueue(4, 324, 6)
    memoryQueue.enqueue(5, 657, 16)
    memoryQueue.printQueue()
    memoryQueue.clear()        
