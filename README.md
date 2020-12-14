# NaiveRPC
NaiveRPC, Rutgers CS 552 Course Project



## Introduction

Follwing is the organization of this repository:

```
.
├── LICENSE
├── NaiveRPC
│   ├── __init__.py
│   ├── client.py  # definition of Client class
│   ├── crypto.py  # crypto library*
│   ├── function.py  # definition of Function and FunctionPool classes
│   ├── server.py  # definition of Server, ThreadServer and ThreadPoolServer classes
│   └── utils.py  # utility functions and how server handle requests
├── README.md
└── test
    ├── client.py  # test client
    ├── samples.py  # sample functions ready to be used by test server
    └── server.py  # test server
```

 

- The crypto library is not implemented by us, we borrowed it from this [source](https://hackernoon.com/how-to-use-aes-256-cipher-python-cryptography-examples-6tbh37cr)



## Environment

- We develope with Python v3.7.1:260ec2c36a and tested on following environments:

```
[1] Darwin Kernel Version 20.1.0: Sat Oct 31 00:07:11 PDT 2020; root:xnu-7195.50.7~2/RELEASE_X86_64

[2] Linux ubuntu 4.15.0-126-generic #129-Ubuntu SMP Mon Nov 23 18:53:38 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
```

- We used following third-party python libraries:

```
[bayesian-optimization 1.2.0] pip3 install bayesian-optimization
https://pypi.org/project/bayesian-optimization/

[pycryptodomex 3.9.9] pip3 install bayesian-optimization
https://pypi.org/project/pycryptodomex/
```



## A Simple Test

```bash
# Change to test directory
$ cd test

# In one terminal, start the test server
# Notice that "python3" is required
$ python3 server.py --server=thread
# or
$ python3 server.py --server=threadpool

# Open another terminal, start the test client
# Notice that "python3" is required
$ python3 client.py

# You will see messages from both server and client side,
# as well as a well-recorded log in the same folder

# You can also try to run tests interactively
```



## Tutorial

### server side

```python
from NaiveRPC import Function, FunctionPool, RegisterFunction
from NaiveRPC import ThreadServer, ThreadPoolServer

# Prepare your function(s) for RPC service
def f():
  return "A simple function"

# Register your function(s)
F = RegisterFunction(f, public=True, always_return=True)

# Create a FunctionPool
FP = FunctionPool("simple function pool")

# Add the Function to the FunctionPool
FP.add(F)

# Create a server, specify FunctionPool and password
server = ThreadServer("127.0.0.1", 1000, FunctionPool=FP, password="42")

# Start the server
server.start()
```



### client side

```python
from NaiveRPC import Client

# Create a client and connect
client = Client()
client.connect('127.0.0.1', 10000)

# Authentication
client.authenticate("42")

# Examine the basic information
client.print()

# Examine the detailed information
client.print_all()

# Execute a function
client.execute("f()")

# Close the client
client.close()
```



### log

- You should expect a well-formatted log which record the time of events, what are those events and where do they happened.



## Presentations

- Presentation [video](https://rutgers.zoom.us/rec/play/2K4HxVup89GHZRfIY3hNg5io5trPCflvn2i3QHWBHXWVl1LRLATsmkGwW96ELEGs7QlrWJB2jS3Jtoyt.SzbCwkdaXyVZ7cOM?continueMode=true&_x_zm_rtaid=AK5aJ5hYQAawDkZcOTsKBw.1607975612936.42f85a688eddffc5daacb0ceb0041677&_x_zm_rhtaid=918)

- Demostration [video](https://rutgers.zoom.us/rec/play/FkCpHaz5nWC7M0bH1isvsqtFVSMKZdh0_gNF65xoeMxnUdTNTsV8_g1RP0VdA_1gV9KkIGVSXXBUJQmt.WTQS8rKglKsHIat3?continueMode=true&_x_zm_rtaid=NvxQRyMgRFeqeMNfzhyUhw.1607978532139.734bc9a1e132abca9fd180e49bf369b2&_x_zm_rhtaid=603)



## Group members

```
Wenjie Qiu: wenjie.qiu@rutgers.edu

Yunhao Shi: ys536@rutgers.edu

Sen Zhang: sz519@rutgers.edu
```