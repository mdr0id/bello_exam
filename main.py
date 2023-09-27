from producer import Producer
from consumer import Consumer
from buffer import Buffer
import logging

"""
Main is used to design the producer, buffer, and consumer message flows.

Implementation details:
    Main is used as the driver for the current message window. In this case
    we assumed the apps are communicating over threads, but this could be 
    implemented with sockets or other communications to remove the internal 
    threading per application. The below case is used to simulate one buffer with
    one producer and one consumer. This could be vertically scaled but additional
    tests would need to be added. However since the buffers are thread safe, we have
    flexibility to implement other designs.

Usage: python3 main.py

CASE 1:
    buff = Buffer(10)
    p1 = Producer(2, buff, 0)
    c1 = Consumer(10, buff, 0)

    This is the default case but this can be toggled depending on the users debugging.

CASE 2:
    buff = Buffer(10)
    p1 = Producer(2, buff, 1) #any number greater than 0 will generate this subset of timestamps
    c1 = Consumer(10, buff, 0)

    This is the bonus case for generating random timestamps from the producer.

CASE 3:
    buff = Buffer(10)
    p1 = Producer(2, buff, 9999) #any number greater than 0 will generate this subset of timestamps
    c1 = Consumer(10, buff, 10) #any number greater than 0 will sum this delta of metrics passed current time

    This is the additional bonus case of generating time based metrics per some delta.

"""

def main():
    # create logger
    logger = logging.getLogger('Main')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    buff = Buffer(10)
    p1 = Producer(2, buff, 0)
    c1 = Consumer(10, buff, 0)
    logger.debug("Starting 1 Producer; 1 Consumer.")
    logger.debug("Buffer max size: %i \n", buff.maxSize)
    p1.start()
    c1.start()
    p1.join()
    c1.join()

if  __name__ == "__main__":
    main()
