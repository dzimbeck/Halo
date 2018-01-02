import multiprocessing
from multiprocessing import Process
import threading

class ThreadRunner(threading.Thread):
    """ This class represents a single instance of a running thread"""
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
    def run(self):
        print self.name,'\n'

class ProcessRunner:
    """ This class represents a single instance of a running process """
    def runp(self, pid, numThreads):
        mythreads = []
        for tid in range(numThreads):
            name = "Proc-"+str(pid)+"-Thread-"+str(tid)
            th = ThreadRunner(name)
            mythreads.append(th) 
        for i in mythreads:
            i.start()
        for i in mythreads:
            i.join()

class ParallelExtractor:    
    def runInParallel(self, numProcesses, numThreads):
        myprocs = []
        prunner = ProcessRunner()
        for pid in range(numProcesses):
            pr = Process(target=prunner.runp, args=(pid, numThreads)) 
            myprocs.append(pr) 
#        if __name__ == 'parallelTestModule':    #This didnt work
#        if __name__ == '__main__':              #This obviously doesnt work
#        multiprocessing.freeze_support()        #added after seeing error to no avail
        for i in myprocs:
            i.start()

        for i in myprocs:
            i.join()