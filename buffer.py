import time
import logging

"""

Buffer class used to cache inbound messages from a producer and
allow a consumer to retrieve them. The buffer is a FIFO queue.

Implementation Details:
    The buffer class will default to a maxsize of 1 if invalid parameters
    are provided to graceful operation. Also if many producers or one producer
    is sending more than the compacity of the buffer, the buffer will drop this
    item and remove the oldest timestamp item. Depending on the implementation
    this likely could be handled better with some ACK protocol. Essentially, the
    buffer could respond to the producer that it was not able to store the sent txn
    and please try again. 
    
    The remove oldest timestamp logic assumes that there was one producer and one 
    consumer, but is setup for N producers and N comsumers. In the one producer and 
    one consumer best case we could assume the oldest timestamp was the first one sent
    and would not need to iterate over the timestamps because we only have one inbound
    message flow. In the case were we have many producers, we can not assume that the
    oldest timestamp is always the first one inbound to the queue. We could have a case
    were many producers are sending higher rates of inbound messages and segmenting intervals
    of oldest timestamps. 

    Finally, if this list was serving as a larger cache it could be implemented as a dictionary
    to reduce lookup times to some degree. However there is also a case to where we could vertically
    scale the buffers to serve many producer or consumers, so it depends on the requirements of 
    the system.

"""
class Buffer:
    def __init__(self, maxSize=1):
        # create logger
        self.logger = logging.getLogger('<BUFF>')
        self.logger.setLevel(logging.DEBUG)
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.ch.setFormatter(self.formatter)
        self.logger.addHandler(self.ch)
        self.items = []
        
        if maxSize <= 0:
            self.logger.error("invalid maxSize, setting to 1 to continue")
            self.maxSize = 1
        else:
            self.maxSize = maxSize
        
       
    def isEmpty(self):
        return len(self.items) == 0
    
    
    def isFull(self):
        return len(self.items) == self.maxSize
    
    
    def displayAllItems(self):
        if not self.isEmpty():
            for item in self.items:
                self.logger.debug("%s",item)

        
    def removeOldItem(self):
        oldItem = self.items[0]["rec_time"]
        oldId = 0

        #self.displayAllItems()

        #remove the oldest recieved timestamp txn
        index = 0
        for item in self.items:
            if oldItem >= item["rec_time"]:
                oldItem = item["rec_time"]
                oldId = index
            index+=1

        self.logger.debug("\t isFull REMOVING %s", self.items[oldId])
        del self.items[oldId]

        #verify removal
        #self.displayAllItems()

    def put(self, item):
        item["rec_time"] = time.time()
        if self.isFull() == False:
            self.items.insert(0,item)
            self.logger.debug("size: %i", self.size())
        else:
            self.logger.debug("isFull - DROPPING txn: %s", item )
            self.removeOldItem()
            

    def get(self):
        return self.items.pop()
    
    def top(self):
        return self.items[0] if len(self.items) > 0 else 0

    def size(self):
        return len(self.items)
