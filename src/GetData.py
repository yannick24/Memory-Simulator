'''
Created on Sep 26, 2011

@author: yannick
'''

from CustomQueue import MyQueue

class ReadData():
    '''
    class used to read text file containing data
    '''

    def __init__(self, filename = "test_jobs.txt"):
        '''
        Constructor
        '''
        self.filename = filename
        self.entryQueue = MyQueue()
        
    '''
    Check if file exists or not
    '''
    def fileExists(self, filename):
        try:
            f = open(filename)
            f.close()
            return True
        except IOError:
            return False
    
    '''
    Read data from text file and store it in an instance of my Custom Queue
    Return Custom Queue object
    '''    
    def readDataFile(self, filename):
        if (self.fileExists(filename)):
            try:
                f = open(filename, "r")
                line = f.readline()
                
                while line != '':
                    line = line.strip()
                    
                    # for debugging purpose
                    # print line 
                    
                    # case : if blank line
                    if (len(line) == 0):
                        line = f.readline()
                        continue
                    # case : if comment line
                    if (line[0] == '#'):
                        line = f.readline()
                        continue
                    # case : if data line
                    jobProcess = line.split() 
                    if (len(jobProcess) > 3):
                        self.entryQueue.enqueue(jobProcess[0], jobProcess[1], jobProcess[2])
                   
                    # for debugging purpose
                    # print jobProcess
                    
                    line = f.readline()
                    
                f.close()
            except IOError:
                return "Cannot open File..."
        return "File is not found..."
    
    
    
    
if __name__ == '__main__':
    data = ReadData()
    try:
        data.readDataFile(data.filename)
        data.entryQueue.printQueue()
    except IOError:
        print "error"