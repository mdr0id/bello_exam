# Technical Coding Challenge: Data Pipeline
All of the included python files contain detailed explanation in the top comment block.

This implmentation assumes 1 producer, 1 buffer, and 1 consumer using threading approach in main.py.

## Usage:

`python3 main.py`

### Case 1 (main.py: line 52-54):
```
    buff = Buffer(10)
    p1 = Producer(2, buff, 0)
    c1 = Consumer(10, buff, 0)

    This is the default case but this can be toggled depending on the users debugging.
```

### Case 2 (main.py: line 52-54):
```
    buff = Buffer(10)
    p1 = Producer(2, buff, 1) #any number greater than 0 will generate this subset of timestamps
    c1 = Consumer(10, buff, 0)

    This is the bonus case for generating random timestamps from the producer.
```

### Case 3 (main.py: line 52-54):
```
    buff = Buffer(10)
    p1 = Producer(2, buff, 9999) #any number greater than 0 will generate this subset of timestamps
    c1 = Consumer(10, buff, 10) #any number greater than 0 will sum this delta of metrics passed current time

    This is the additional bonus case of generating time based metrics per some delta.
```
### Debug Flow
The initial test was to design a single producer creating a message each second and ensuring the buffer recived that
message once `put` was used. Once this was confirmed it was set into a threaded while loop to poll for the duration
of the process. The buffer class was then to confirmed to have valid functions (e.g. isEmpty, isFull, size, put, top, get).
Once the buffer had items, the consumer was isolated to follow this same flow and ensure it could consume items in the buffer.
When that was valid it too was put into a threaded while loop for the duration of the process.

Once both ends of the message protocol were stable, I began checking configurable intervals to sanity check starving messages, prodcuing too many messages for dropping, and removing older timestamps. This allowed me to see the current window of message flows and design the producer and consumer on a sliding window design to simplify the time based metrics and random epochs.

The final checks were to ensure the bounds of the classes were ensured. Much of these iterations were passing negative polling intervals, negative random polling intervals, and empty buffers into these classes. Depending on the usage it might make more sense to have negative random intervals to better convey current time minus that delta but for simplicity we only assume positive deltas subtracted from current time. 
