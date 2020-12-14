import socket 
import sys

sys.path.append('..')
from NaiveRPC import Client


def main():

    # creat client and connect
    client = Client()
    client.connect('127.0.0.1', 10000)

    # authentication
    client.authenticate("42")  # password of server
    
    # check the status and content of the FunctionPool binded with the server
    client.print()
    client.print_all()

    # execute functions by sending command
    client.execute("optimization()")
    client.execute("black_box_function(5,5)")
    client.execute("square(1000)")
    client.execute("distance(0, 0, 1, 1)")
    client.execute("rev_string('this is a string!')")
    client.execute("cat_string('string_1', 'string_2')")
    client.execute("print_dictionary({'key1':111, 'key2':222, 'key3':333})")

    # malicious function calls
    client.execute("error command")
    client.execute("not_this_function(1, 1)")

    client.close()


if __name__ == '__main__':
    main()
