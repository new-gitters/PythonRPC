import os
import sys
import inspect
import argparse

sys.path.append('..')
from NaiveRPC import ThreadServer, ThreadPoolServer
from samples import FP


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", type=str, choices=('thread','threadpool'), required=True, help="select a type of server: thread/threadpool")

    args = parser.parse_args()
    return args


def main(args):

    if args.server == "thread":
        server = ThreadServer('127.0.0.1', 10000, FunctionPool=FP, password="42")  # password of server
    elif args.server == "threadpool":
        server = ThreadPoolServer('127.0.0.1', 10000, FunctionPool=FP, password="42")  # password of server

    server.start()


if __name__ == '__main__':
    args = parse()
    main(args)
