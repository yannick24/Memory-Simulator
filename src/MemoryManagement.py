'''
Created on Sep 26, 2011

@author: yannick
'''

from MemoryPartition import MyPartition
from GetData import ReadData
from CustomQueue import MyQueue
from CustomQueue import MyElt

class MyMemory():
    '''
    class used to simulate memory management for best-fit, first-fit, and next-fit
    '''

    def __init__(self, space = 16384, os = 4096):
        '''
        Constructor
        '''
        self.space = space  # total space of memory
        self.os = os        # space of OS in memory
        
        self.elapsedTime = 0
        self.jobProcessed = 0
        
        # create OS partition and free partition called "main"
        # double link partition in memory
        self.osPartition = MyPartition("OS partition", 4096, "Undefined", "OS", [0, self.os])
        self.mainPartition = MyPartition("blank partition", 12288, 0, "Available", [self.os , self.space]) 
        self.osPartition.nextPartition = self.mainPartition
        self.mainPartition.prevPartition = self.osPartition
        
        # get data from text file and put them in entry queue
        dataQueue = ReadData()
        dataQueue.readDataFile(dataQueue.filename)
        self.entryQueue = MyQueue()
        self.entryQueue = dataQueue.entryQueue
        
        # variables used to compute statistics of best-fit, first-fit, and next-fit
        self.entryQueueLength = {}
        self.memoryRatio = {}
        self.fragmentation = {}
        
        # variable used to store memory output
        self.output = ''
        
    '''
    insert job using first-fit algorithm
    '''
    def insertProcessFirstFit(self, number, size, duration):
        memoryPartition = self.osPartition
        
        while(True):            
            # partition is OS: just skip to the next partition
            if (memoryPartition.status == "OS"):
                memoryPartition = memoryPartition.nextPartition
                continue

            # partition is not blank partition skip
            if (memoryPartition.status != "Available"):
                if (self.checkAvailableSpace(memoryPartition)):
                    memoryPartition = memoryPartition.nextPartition
                    continue
                # reach end of memory
                else:
                    self.updateMemory()
                    # calculation of fragmentation over time
                    fragmentation = self.findFragmentation()
                    if (fragmentation != None):
                        self.fragmentation[self.elapsedTime] = fragmentation
                    while (not(self.checkProcessIfDone())):
                        self.updateMemory()
                    done = self.insertProcessFirstFit(number, size, duration)
                    if(done): # insertion is done
                        return True
            
            # if partition is blank check size: if enough put new process in 
            if (memoryPartition.status == "Available"):
                if (memoryPartition.size > int(size[0:-1])):
                    memoryPartition.name = "Process " + number
                    memoryPartition.duration = duration
                    memoryPartition.status = "Processing"
                    memoryPartition.space = [memoryPartition.space[0], memoryPartition.space[0] + int(size[0:-1])]
                    if (self.checkAvailableSpace(memoryPartition)):
                        nextPartition = memoryPartition.nextPartition
                        newNextPartition = MyPartition("blank partition", memoryPartition.size - int(size[0:-1]), 0, "Available", 
                                                        [memoryPartition.space[0] + int(size[0:-1]), memoryPartition.space[0] + memoryPartition.size])
                        memoryPartition.size = int(size[0:-1])
                        memoryPartition.nextPartition = newNextPartition
                        newNextPartition.prevPartition = memoryPartition
                        newNextPartition.nextPartition = nextPartition
                        nextPartition.prevPartition = newNextPartition
                        if(not(self.entryQueue.isEmpty())):
                            self.output += "=> Time spent in entry queue for job " + str(self.entryQueue.frontElt().itemNumber) + ": " + str(self.entryQueue.frontElt().timeInQueue) + "\n"
                            print "=> Time spent in entry queue for job ", self.entryQueue.frontElt().itemNumber, ": ", self.entryQueue.frontElt().timeInQueue
                        self.entryQueue.dequeue()
                        self.entryQueueLength[self.elapsedTime] = self.entryQueue.length
                        return True
                    
                    # reach end of memory
                    else:
                        newNextPartition = MyPartition("blank partition", memoryPartition.size - int(size[0:-1]), 0, "Available", 
                                                        [memoryPartition.space[0] + int(size[0:-1]), memoryPartition.space[0] + memoryPartition.size])
                        memoryPartition.size = int(size[0:-1])
                        memoryPartition.nextPartition = newNextPartition
                        newNextPartition.prevPartition = memoryPartition
                        if(not(self.entryQueue.isEmpty())):
                            self.output += "=> Time spent in entry queue for job " + str(self.entryQueue.frontElt().itemNumber) + ": " + str(self.entryQueue.frontElt().timeInQueue) + "\n"
                            print "=> Time spent in entry queue for job ", self.entryQueue.frontElt().itemNumber, ": ", self.entryQueue.frontElt().timeInQueue
                        self.entryQueue.dequeue()
                        self.entryQueueLength[self.elapsedTime] = self.entryQueue.length
                        return True
                        
                if (memoryPartition.size == size[0:-1]):
                    memoryPartition.name = "Process " + number
                    memoryPartition.duration = duration
                    memoryPartition.status = "Processing"
                    if(not(self.entryQueue.isEmpty())):
                        self.output += "=> Time spent in entry queue for job " + str(self.entryQueue.frontElt().itemNumber) + ": " + str(self.entryQueue.frontElt().timeInQueue) + "\n"
                        print "=> Time spent in entry queue for job ", self.entryQueue.frontElt().itemNumber, ": ", self.entryQueue.frontElt().timeInQueue
                    self.entryQueue.dequeue()
                    self.entryQueueLength[self.elapsedTime] = self.entryQueue.length
                    return True
                
                if (memoryPartition.size < size[0:-1]):
                    if (self.checkAvailableSpace(memoryPartition)):
                        memoryPartition = memoryPartition.nextPartition
                        continue
                    # reach end of memory
                    else:
                        self.updateMemory()
                        # calculation of fragmentation over time
                        fragmentation = self.findFragmentation()
                        if (fragmentation != None):
                            self.fragmentation[self.elapsedTime] = fragmentation
                        while (not(self.checkProcessIfDone())):
                            self.updateMemory()
                        done = self.insertProcessFirstFit(number, size, duration)
                        if(done): # insertion is done
                            return True
                
                    
            # check space to make sure partition does not go out of memory bounds
            # if we reach end of memory, and memory is full: Update memory => need boolean variable for 
            
    '''
    insert job using best-fit algorithm
    '''        
    def insertProcessBestFit(self, number, size, duration):
        # check if there is partition in memory
        partition = self.traverseMemory(int(size[0:-1]))
        # case : partition exists
        if (partition != None):
            if (partition.size == int(size[0:-1])):
                partition.name = "Process " + number
                partition.duration = duration
                partition.status = "Processing"
                if(not(self.entryQueue.isEmpty())):
                    self.output += "=> Time spent in entry queue for job " + str(self.entryQueue.frontElt().itemNumber) + ": " + str(self.entryQueue.frontElt().timeInQueue) + "\n"
                    print "=> Time spent in entry queue for job ", self.entryQueue.frontElt().itemNumber, ": ", self.entryQueue.frontElt().timeInQueue
                self.entryQueue.dequeue()
                self.entryQueueLength[self.elapsedTime] = self.entryQueue.length
                return True
            if (partition.size > int(size[0:-1])):
                partition.name = "Process " + number
                partition.duration = duration
                partition.status = "Processing"
                partition.space = [partition.space[0], partition.space[0] + int(size[0:-1])]
                if (self.checkAvailableSpace(partition)):
                    nextPartition = partition.nextPartition
                    newNextPartition = MyPartition("blank partition", partition.size - int(size[0:-1]), 0, "Available", 
                                                    [partition.space[0] + int(size[0:-1]), partition.space[0] + partition.size])
                    partition.size = int(size[0:-1])
                    partition.nextPartition = newNextPartition
                    newNextPartition.prevPartition = partition
                    newNextPartition.nextPartition = nextPartition
                    nextPartition.prevPartition = newNextPartition
                    if(not(self.entryQueue.isEmpty())):
                        self.output += "=> Time spent in entry queue for job " + str(self.entryQueue.frontElt().itemNumber) + ": " + str(self.entryQueue.frontElt().timeInQueue) + "\n"
                        print "=> Time spent in entry queue for job ", self.entryQueue.frontElt().itemNumber, ": ", self.entryQueue.frontElt().timeInQueue
                    self.entryQueue.dequeue()
                    self.entryQueueLength[self.elapsedTime] = self.entryQueue.length
                    return True
                else:
                    newNextPartition = MyPartition("blank partition", partition.size - int(size[0:-1]), 0, "Available", 
                                                    [partition.space[0] + int(size[0:-1]), partition.space[0] + partition.size])
                    partition.size = int(size[0:-1])
                    partition.nextPartition = newNextPartition
                    newNextPartition.prevPartition = partition
                    if(not(self.entryQueue.isEmpty())):
                        self.output += "=> Time spent in entry queue for job " + str(self.entryQueue.frontElt().itemNumber) + ": " + str(self.entryQueue.frontElt().timeInQueue) + "\n"
                        print "=> Time spent in entry queue for job ", self.entryQueue.frontElt().itemNumber, ": ", self.entryQueue.frontElt().timeInQueue
                    self.entryQueue.dequeue()
                    self.entryQueueLength[self.elapsedTime] = self.entryQueue.length
                    return True
        # case : partition does not exist
        else:
            self.updateMemory()
            # calculation of fragmentation over time
            fragmentation = self.findFragmentation()
            if (fragmentation != None):
                self.fragmentation[self.elapsedTime] = fragmentation
            while (not(self.checkProcessIfDone())):
                self.updateMemory()
            done = self.insertProcessBestFit(number, size, duration)
            if(done): # insertion is done
                return True
        
    
    '''
    traverse memory and look for smallest partition to put job
    '''
    def traverseMemory(self, size):
        partition = self.mainPartition
        bestPartition = MyPartition("temp", 0)
        closest = 0
        findOnePartition = False    # boolean variable to check for success or failure
        
        # go through main partition
        while(partition):
            if(partition.status == "Available" and partition.size >= size):
                if (findOnePartition):
                    if (closest > partition.size - size):
                        bestPartition = partition
                        closest = partition.size - size
                else:
                    bestPartition = partition
                    closest = partition.size - size
                    findOnePartition = True
            partition = partition.nextPartition
        if (not(findOnePartition)):
            return None
        return bestPartition
    
    '''
    insert job using next-fit algorithm
    '''
    def insertProcessNextFit(self, number, size, duration):
        # look through main memory if it contains job already
        partition = self.lookForLastJob()
        # case : if it contains job, starts from last job in memory 
        if (partition != None):
            if (self.checkAvailableSpace(partition)):
                partition = partition.nextPartition
            else:
                partition = self.mainPartition
            while (partition):
                if (partition.status == "Available"):
                    if (partition.size > int(size[0:-1])):
                        partition.name = "Process " + number
                        partition.duration = duration
                        partition.status = "Processing"
                        partition.space = [partition.space[0], partition.space[0] + int(size[0:-1])]
                        if (self.checkAvailableSpace(partition)):
                            nextPartition = partition.nextPartition
                            newNextPartition = MyPartition("blank partition", partition.size - int(size[0:-1]), 0, "Available", 
                                                        [partition.space[0] + int(size[0:-1]), partition.space[0] + partition.size])
                            partition.size = int(size[0:-1])
                            partition.nextPartition = newNextPartition
                            newNextPartition.prevPartition = partition
                            newNextPartition.nextPartition = nextPartition
                            nextPartition.prevPartition = newNextPartition
                            if(not(self.entryQueue.isEmpty())):
                                self.output += "=> Time spent in entry queue for job " + str(self.entryQueue.frontElt().itemNumber) + ": " + str(self.entryQueue.frontElt().timeInQueue) + "\n"
                                print "=> Time spent in entry queue for job ", self.entryQueue.frontElt().itemNumber, ": ", self.entryQueue.frontElt().timeInQueue
                            self.entryQueue.dequeue()
                            self.entryQueueLength[self.elapsedTime] = self.entryQueue.length
                            return True
                    
                        # reach end of memory
                        else:
                            newNextPartition = MyPartition("blank partition", partition.size - int(size[0:-1]), 0, "Available", 
                                                        [partition.space[0] + int(size[0:-1]), partition.space[0] + partition.size])
                            partition.size = int(size[0:-1])
                            partition.nextPartition = newNextPartition
                            newNextPartition.prevPartition = partition
                            if(not(self.entryQueue.isEmpty())):
                                self.output += "=> Time spent in entry queue for job " + str(self.entryQueue.frontElt().itemNumber) + ": " + str(self.entryQueue.frontElt().timeInQueue) + "\n"
                                print "=> Time spent in entry queue for job ", self.entryQueue.frontElt().itemNumber, ": ", self.entryQueue.frontElt().timeInQueue
                            self.entryQueue.dequeue()
                            self.entryQueueLength[self.elapsedTime] = self.entryQueue.length
                            return True
                        
                    if (partition.size == size[0:-1]):
                        partition.name = "Process " + number
                        partition.duration = duration
                        partition.status = "Processing"
                        if(not(self.entryQueue.isEmpty())):
                            self.output += "=> Time spent in entry queue for job " + str(self.entryQueue.frontElt().itemNumber) + ": " + str(self.entryQueue.frontElt().timeInQueue) + "\n"
                            print "=> Time spent in entry queue for job ", self.entryQueue.frontElt().itemNumber, ": ", self.entryQueue.frontElt().timeInQueue
                        self.entryQueue.dequeue()
                        self.entryQueueLength[self.elapsedTime] = self.entryQueue.length
                        return True
                    
                    if (partition.size < size[0:-1]):
                        if (self.checkAvailableSpace(partition)):
                            partition = partition.nextPartition
                            continue
                        # reach end of memory
                        else:
                            self.updateMemory()
                            # calculation of fragmentation over time
                            fragmentation = self.findFragmentation()
                            if (fragmentation != None):
                                self.fragmentation[self.elapsedTime] = fragmentation
                            while (not(self.checkProcessIfDone())):
                                self.updateMemory()
                            done = self.insertProcessNextFit(number, size, duration)
                            if(done): # insertion is done
                                return True
        # case : if it does not contain job in memory
        elif (not(self.hasJobProcessing())):
            partition = self.mainPartition
            if (partition.size == int(size[0:-1])):
                partition.name = "Process " + number
                partition.duration = duration
                partition.status = "Processing"
                if(not(self.entryQueue.isEmpty())):
                    self.output += "=> Time spent in entry queue for job " + str(self.entryQueue.frontElt().itemNumber) + ": " + str(self.entryQueue.frontElt().timeInQueue) + "\n"
                    print "=> Time spent in entry queue for job ", self.entryQueue.frontElt().itemNumber, ": ", self.entryQueue.frontElt().timeInQueue
                self.entryQueue.dequeue()
                self.entryQueueLength[self.elapsedTime] = self.entryQueue.length
                return True
            if (partition.size > int(size[0:-1])):
                partition.name = "Process " + number
                partition.duration = duration
                partition.status = "Processing"
                partition.space = [partition.space[0], partition.space[0] + int(size[0:-1])]
                newNextPartition =  MyPartition("blank partition", partition.size - int(size[0:-1]), 0, "Available", 
                                                    [partition.space[0] + int(size[0:-1]), partition.space[0] + partition.size])
                partition.size = int(size[0:-1])
                partition.nextPartition = newNextPartition
                newNextPartition.prevPartition = partition
                if(not(self.entryQueue.isEmpty())):
                    self.output += "=> Time spent in entry queue for job " + str(self.entryQueue.frontElt().itemNumber) + ": " + str(self.entryQueue.frontElt().timeInQueue) + "\n"
                    print "=> Time spent in entry queue for job ", self.entryQueue.frontElt().itemNumber, ": ", self.entryQueue.frontElt().timeInQueue
                self.entryQueue.dequeue()
                self.entryQueueLength[self.elapsedTime] = self.entryQueue.length
                return True
    
    '''
    look if there is some job in memory
    '''
    def lookForLastJob(self):
        partition = self.mainPartition
        foundJob = False
        
        # go through main partition
        while (partition):
            if (partition.status == "Processing"):
                lastJobInMemory = partition
                foundJob = True
            partition = partition.nextPartition
        if (foundJob):
            return lastJobInMemory
        return None
            
    '''
    check if there is partition after a specified partition 
    specified partition passed as argument
    '''
    def checkAvailableSpace(self, partition):
        temp = MyPartition("temp", 0)
        temp = partition
        if (temp.nextPartition == None):
            return False
        return True
    
    '''
    increment and decrement time 
    
    '''
    def updateMemory(self):
        # go through each job in memory and decrement duration
        temp = self.mainPartition
        while (temp):
            if (temp.status == "Processing"):
                temp.duration = int(temp.duration) - 1
            temp = temp.nextPartition
            
        # go through each job in entry queue and increment waiting time
        temp = MyElt()
        temp = self.entryQueue.frontElt()
        while (temp):
            temp.timeInQueue = int(temp.timeInQueue) + 1
            temp = temp.nextItem
            
        # increment elapsed time
        self.elapsedTime = int(self.elapsedTime) + 1
        
    '''
    Compute memory in use over time
    when memory cannot load the next job
    '''    
    def findMemoryInUse(self):
        # go through each job in memory and decrement duration
        temp = self.mainPartition
        memoryInUse = 0
        while (temp):
            if (temp.status == "Processing"):
                memoryInUse += temp.size
            temp = temp.nextPartition
        return memoryInUse
    
    '''
    Find fragmentation in memory over time
    return number of fragmentation with average size
    '''
    def findFragmentation(self):
        # go through each job in memory and decrement duration
        temp = self.mainPartition
        numFrag = 0
        size = 0
        while (temp):
            if (temp.status == "Available"):
                numFrag += 1
                size += temp.size
            temp = temp.nextPartition
        if (numFrag > 0):
            averageSize = float(size) / numFrag 
            return [numFrag, averageSize]
        return None
    
    '''
    remove job in memory when it is done
    check if the next or previous partition are blank and converge them if it is true
    '''
    def removeProcess(self, partition):
        temp = MyPartition("temp", 0)
        temp = partition
        temp.name = "blank partition"
        temp.duration = 0
        temp.status = "Available"
        if (temp.prevPartition != None):
            prevPart = MyPartition("temp", 0)
            prevPart = temp.prevPartition
            if (prevPart.status == "Available"):
                temp = self.combineBlankPartition(prevPart, temp)
        if (partition.nextPartition != None):
            nextPart = MyPartition("temp", 0)
            nextPart = temp.nextPartition
            if (nextPart.status == "Available"):
                temp = self.combineBlankPartition(temp, nextPart)
        # if there is no jobs processing in memory and partitions were not merged correctly
        if (not(self.hasJobProcessing())):
            self.mainPartition = MyPartition("blank partition", 12288, 0, "Available", [self.os , self.space]) 
            self.osPartition.nextPartition = self.mainPartition
            self.mainPartition.prevPartition = self.osPartition
        self.checkProcessIfDone()
        
    '''
    converge blank partition
    '''
    def combineBlankPartition(self, partition1, partition2):
        temp = MyPartition("temp", 0)
        temp = partition1
        partition1 = temp
        temp = partition2
        partition2 = temp
        if (partition1.status == "Available" and partition2.status == "Available"):
            if (partition1.space[1] == partition2.space[0]):
                partition1.nextPartition = partition2.nextPartition
                partition1.size += partition2.size
                partition1.space[1] = partition2.space[1]
                return partition1
    
    '''
    check if some jobs are done in memory or not
    if so, remove them and return True
    false otherwise
    '''
    def checkProcessIfDone(self):
        memoryPartition = self.mainPartition
        while(memoryPartition):
            if(memoryPartition.status == "Processing"):
                if (memoryPartition.duration == 0):
                    # computation of memory ratio goes HERE
                    memoryInUse = self.findMemoryInUse()
                    self.memoryRatio[self.elapsedTime] = memoryInUse
                    
                    # calculation of fragmentation over time
                    fragmentation = self.findFragmentation()
                    if (fragmentation != None):
                        self.fragmentation[self.elapsedTime] = fragmentation
                    
                    # increment job processed
                    self.jobProcessed = int(self.jobProcessed) + 1
                    
                    self.removeProcess(memoryPartition)
                    return True
            memoryPartition = memoryPartition.nextPartition
        return False
    
    '''
    print content of memory 
    '''
    def printMemoryPartition(self):
        temp = self.osPartition
        # print ">> Name: \t\t\t Size: \t\t\t Status:"
        while (temp):
            print ">> ", temp.name, "\t\t\t", temp.size, "K\t\t\t", temp.status, "\t\t\t", temp.duration
            temp = temp.nextPartition
        print
        print "Job processed: ", self.jobProcessed
        print "Elapsed time: ", self.elapsedTime, "fortnights"
        return "Job processed: " + str(self.jobProcessed) + "\nElapsed time: " + str(self.elapsedTime) + "fortnights"
        
    '''
    check if memory still has some job processing
    return true, if it does
    false otherwise
    '''
    def hasJobProcessing(self):
        temp = self.mainPartition
        while(temp):
            if (temp.status == "Processing"):
                return True
            temp = temp.nextPartition
        return False
    
    '''
    Write data into a text file
    '''
    def writeDataFile(self, filename, content):
        try:
            f = open(filename, "w")
            f.write(content)
            f.close()
        except IOError:
            pass
    
    '''
    simulate memory management
    '''
    def simulation(self, process, algorithm):
        self.output += algorithm + ' Algorithm \n\n'
        while (process):
            if (algorithm == "First-Fit"):
                self.insertProcessFirstFit(process.itemNumber, process.size, process.duration)
            elif (algorithm == "Best-Fit"):
                self.insertProcessBestFit(process.itemNumber, process.size, process.duration)
            elif (algorithm == "Next-Fit"):
                self.insertProcessNextFit(process.itemNumber, process.size, process.duration)
            process = self.entryQueue.frontElt()
                # for debugging purpose 
            # print
            # self.printMemoryPartition()
            # print
          
        while (self.hasJobProcessing()):
            self.checkProcessIfDone()
            if (self.hasJobProcessing()):
                self.updateMemory()    
            # for debugging purpose 
            # print
            # self.printMemoryPartition()
            # print
    
        # if there is no jobs processing in memory
        if (not(self.hasJobProcessing())):
            self.mainPartition = MyPartition("blank partition", 12288, 0, "Available", [self.os , self.space]) 
            self.osPartition.nextPartition = self.mainPartition
            self.mainPartition.prevPartition = self.osPartition
    
    
        # self.printMemoryPartition()
    
    
        throughput = float(self.jobProcessed) / self.elapsedTime
    
        print
        self.output += "\n" + self.printMemoryPartition() + "\n"
        self.output += str('\n=> Throughput: %4.2f \n\n' % throughput)
        # print '=> Throughput: %4.2f \n' % throughput
    
        for key, value  in self.entryQueueLength.iteritems():
            # print '=> at t = ',key, ' fortnights: ', value, ' job in Entry Queue'
            self.output += '=> at t = ' + str(key) + ' fortnights: ' + str(value) + ' job in Entry Queue\n'
        
        print
        self.output += '\n'
    
        for key, value  in self.memoryRatio.iteritems():
            # print '=> at t = ',key, ' fortnights:  %4.2f percent of memory in use. (main partition: OS excluded)' % ((float(value) /( self.space - self.os )) * 100)
            self.output += str('=> at t = ' + str(key) + ' fortnights:  %4.2f percent of memory in use. (main partition: OS excluded)\n' % ((float(value) /( self.space - self.os )) * 100))
    
        print
        self.output += '\n'
    
        for key, value  in self.fragmentation.iteritems():
            # print '=> at t = ',key, ' fortnights: \n\t- ', value[0], ' number of unused memory\n\t- ', value[1], 'k average size \n'
            self.output += '=> at t = ' + str(key) + ' fortnights: \n\t- ' + str(value[0]) + ' number of unused memory\n\t- ' + str(value[1]) + 'k average size \n'


    
if __name__ == '__main__':
    memory1 = MyMemory()
    memory1.entryQueue.printQueue()
    process = MyElt() 
    
    process = memory1.entryQueue.frontElt()
    
    memory1.simulation(process, "Best-Fit")
    
    print "=================================Best_Fit====================================\n"
    
    #print memory1.output
    memory1.writeDataFile("best_Fit.txt", memory1.output)
    
    
    memory2 = MyMemory()
    process = MyElt() 
    
    process = memory2.entryQueue.frontElt()
    
    memory2.simulation(process, "Next-Fit")
    
    print "=================================Next_Fit====================================\n"
    
    #print memory2.output
    memory2.writeDataFile("next_Fit.txt", memory2.output)
    
    
    memory3 = MyMemory()
    process = MyElt() 
    
    process = memory3.entryQueue.frontElt()
    
    memory3.simulation(process, "First-Fit")
    
    print "=================================First_Fit====================================\n"
    
    #print memory3.output
    memory3.writeDataFile("first_Fit.txt", memory1.output)
    
    
    print "Done!!!!!!"
    











    