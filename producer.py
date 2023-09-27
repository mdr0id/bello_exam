import random
import threading
import uuid
import time
import logging
from buffer import *

"""

Producer class is used to generate messages for the Buffer to cache so the 
Consumer class can retrieve these items from the buffer.

Implementation details:
    The Producer class uses the required constraints but also adds a created 
    timestamp to aid message transmission across the architecture. This could
    be useful if the Producer had an ACK protocol with the buffer, but since it
    fire and forget it might not be needed.

    The ids, amounts, and products are randomly generated from a range of specified 
    values in the document prompt. We set the polling interval to produce to 1 so 
    the message transmission can commense. There might be reasons to not produce 
    messages if we were testing many producers toggling transmission rates to one or
    many buffers. The randomInterval is used to produce timestamps from current time
    minus this delta. Other implementations could be used to bound this to another
    subset outside of current time. This implmentation used the current time to aid
    the live window for the message flow.

"""

class Producer(threading.Thread):
    def __init__(self, interval=1, buffer=[], randomInterval=0):
        super(Producer, self).__init__()
         # create logger
        self.logger = logging.getLogger('PROD ->')
        self.logger.setLevel(logging.DEBUG)
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.ch.setFormatter(self.formatter)
        self.logger.addHandler(self.ch)
        
        self.buffer = buffer
        self.producer_list = ['apple','banana','strawberry','grape','pineapple']

        if interval < 0:
            self.logger.error("invalid polling interval, setting to 1 to continue")
            self.interval = 1
        else:
            self.interval = interval
        
        if randomInterval < 0:
            self.logger.error("invalid random interval, setting to 0 to continue")
            self.randomInterval = 0
        else:
            self.randomInterval = randomInterval

        
    def run(self):
        while True:
            currTime = time.time()
            if self.randomInterval == 0:
                item = {"id": int(uuid.uuid1()), 
                        "product": random.choice(self.producer_list), 
                        "amount": random.randint(1,10),
                        "created": currTime}
                self.buffer.put(item)
                self.logger.debug("item: %s", item)
            elif self.randomInterval >= 1:
                 item = {"id": int(uuid.uuid1()), 
                        "product": random.choice(self.producer_list), 
                        "amount": random.randint(1,10),
                        "created": random.uniform(currTime - self.randomInterval, currTime )}
                 self.buffer.put(item)
                 self.logger.debug("item: %s", item)
            else:
                self.logger.error("invalid randomInterval")
            
            #self.logger.debug("top item %s", self.buffer.top())
            #self.logger.debug("buffer size: %i ", self.buffer.size())
            time.sleep(self.interval)