import threading
import time
import logging
from buffer import *

"""
Consumer class used to consume messages from the Buffer class

Implementation details:
    The consumer class can be configured to poll on seconds interval from the interval variable.
    We set this to 1 in case there is invalid input to ensure the consumer is atleast trying to
    consume some message from the buffer. Depending on the requirements it might be reasonable to
    never consume from the buffer to test vertical scaling or full states.

    The deltaInterval is used to calculate some epoch delta back from current window. This could be
    expanded to mutliples in the cases of wanting to know some summation of metrics from current time.
    For this implementation we calculate normal metrics when this variable is 0 and otherwise it is
    calculated to show the window of subset metrics per the entire metrics window.

    The consumer calculates several epoch deltas in case there is a need to verify message delays per some
    tooling (e.g MITM proxy or Wireshark). 

"""

class Consumer(threading.Thread):
    def __init__(self, interval=1, buffer=[], deltaInterval=0):
        super(Consumer, self).__init__()
        # create logger
        self.logger = logging.getLogger('<- CONS')
        self.logger.setLevel(logging.DEBUG)
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.ch.setFormatter(self.formatter)
        self.logger.addHandler(self.ch)

        self.buffer = buffer
        if interval < 0:
            self.logger.error("invalid polling interval, setting to 1 to continue")
            self.interval = 1
        else:
            self.interval = interval
        
        #used to calulate some delta back from current time in epoch
        if deltaInterval < 0:
            self.logger.error("invalid delta interval, setting to 0 to continue")
            self.deltaInterval = 0
        else:
            self.deltaInterval = deltaInterval
        
        self.totalTxns = 0
        self.totalSales = 0
        self.totalSalesPerProd = {}
        self.size = 0
        self.itemLedger = {}


    def run(self):
        while True:
            self.logger.debug("buffer size: %i ", self.buffer.size())
            if not self.buffer.isEmpty():
                item = self.buffer.get()
                item["consumer_rec_time"] = time.time()
                self.logger.debug("buffer size after get: %i ", self.buffer.size())
                self.calcTotalTxns()
                self.calcSales(item["amount"])
                self.calcTotalSalePerProduct(item)
                self.addItem(item)
                self.printMetrics()
            else:
                self.logger.debug("buffer isEmpty, unable to consume")
            if self.deltaInterval >= 1:
                self.calcIntervalMetrics()
            time.sleep(self.interval)


    def addItem(self,item):
        self.itemLedger[self.size]= {}
        self.itemLedger[self.size]['id'] = item["id"]
        self.itemLedger[self.size]['created_time'] = item["created"]
        self.itemLedger[self.size]['buff_rec_time'] = item["rec_time"]
        self.itemLedger[self.size]['consumer_rec_time'] = item["consumer_rec_time"]
        self.itemLedger[self.size]['product'] = item["product"]
        self.itemLedger[self.size]['amount'] = item["amount"]
        self.logger.debug("consumed item: %s ", self.itemLedger[self.size])
        self.size +=1
        self.logger.debug("consumer size: %i ", self.size)
        #self.displayAllItems(

    
    def displayAllItems(self):
        for i in self.itemLedger:
            self.logger.debug("%s ", self.itemLedger[i])
        
    
    def calcIntervalMetrics(self):
        #use a sliding window to calculate current time minues interval block
        #if multiple intervals we needed then we could calculate each interval
        #and interate for that summation window
        currTime = time.time()
        deltaTime = currTime - float(self.deltaInterval)
        self.logger.debug("Last interval: %s to %s duration(epoch): %f", time.ctime(currTime), time.ctime(deltaTime), self.deltaInterval)
        totalIntervalTxns = 0
        totalIntervalSales = 0
        totalIntervalSalesPerProd = {} 
        
        if int(deltaTime) > 0:
            for i in range(self.size):
                if self.itemLedger[i]["consumer_rec_time"] >= deltaTime:
                    totalIntervalTxns +=1
                    totalIntervalSales += self.itemLedger[i]["amount"]
                    key = self.itemLedger[i]["product"]
                    if key in totalIntervalSalesPerProd.keys():
                        totalIntervalSalesPerProd[key] += self.itemLedger[i]["amount"]
                    else:
                        new_item = {key: self.itemLedger[i]["amount"]}
                        totalIntervalSalesPerProd.update(new_item)
        else:
            self.logger.error("invalid EPOCH interval")
            return

        self.logger.debug("\tinterval txn: %i", totalIntervalTxns)
        self.logger.debug("\tinterval sales: %i", totalIntervalSales)
        self.logger.debug("\tinterval products: %s", totalIntervalSalesPerProd)


    def calcTotalTxns(self):
        self.totalTxns += 1


    def calcSales(self, itemNumber):
        self.totalSales += itemNumber


    def calcTotalSalePerProduct(self, item):
        key = item["product"]
        if key in self.totalSalesPerProd.keys():
            self.totalSalesPerProd[key] += item["amount"]
        else:
            new_item = {key: item["amount"]}
            self.totalSalesPerProd.update(new_item)


    def printMetrics(self):
        self.logger.debug("\ttotal txns: %i", self.totalTxns )
        self.logger.debug("\ttotal sales: %i", self.totalSales )
        self.logger.debug("\ttotal sales per prod: %s", self.totalSalesPerProd )