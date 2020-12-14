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

 

- The crypto library is not implemented by us, we borrowed from this [source](https://hackernoon.com/how-to-use-aes-256-cipher-python-cryptography-examples-6tbh37cr)



## Environment

- We develope with Python v3.7.1:260ec2c36a and tested on following environments:

```
[1] Darwin Kernel Version 20.1.0: Sat Oct 31 00:07:11 PDT 2020; root:xnu-7195.50.7~2/RELEASE_X86_64

[2] Linux ubuntu 4.15.0-126-generic #129-Ubuntu SMP Mon Nov 23 18:53:38 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
```

- Third-party python libraries:

```
[bayesian-optimization 1.2.0] pip3 install bayesian-optimization
https://pypi.org/project/bayesian-optimization/

[pycryptodomex 3.9.9] pip3 install bayesian-optimization
https://pypi.org/project/pycryptodomex/
```

- How to run the test

```bash
# Change to test directory
cd test

# In one terminal, start the test server
# Notice that "python3" is required
$ python3 server.py --server=thread
# or
$ python3 server.py --server=threadpool

# Open another terminal, start the test client
$ python3 client.py

# You will see messages from both server and client side,
# as well as a well-recorded log in the same folder

# You can also try to run tests interactively
```



## Presentations

- Presentation video: 





## Group members

```
Wenjie Qiu: wenjie.qiu@rutgers.edu

Yunhao Shi: ys536@rutgers.edu

Sen Zhang: sz519@rutgers.edu
```