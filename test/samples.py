import math
import sys

from bayes_opt import BayesianOptimization

sys.path.append('..')
from NaiveRPC import Function, FunctionPool, RegisterFunction


def square(x):
    '''
    return the square of a value
    '''
    return x**2


def distance(x1, y1, x2, y2):
    '''
    return the distance of two points
    '''
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)


def black_box_function(x, y):
    '''
    Hidden function
    '''
    return -x ** 2 - (y - 1) ** 2 + 1

def optimization():
    '''
    optimization of black_box_function
    '''
    pbounds = {'x': (2, 4), 'y': (-3, 3)}
    optimizer = BayesianOptimization(
        f=black_box_function,
        pbounds=pbounds,
        random_state=1,
    )

    optimizer.maximize(
        init_points=5,
        n_iter=20,
    )

    return optimizer.res


def rev_string(string):
    
    return ''.join(reversed(string))


def cat_string(string1, string2):

    return string1 + string2


def print_dictionary(dictionary):
    result = ""

    for key in dictionary:
        result += key
        result += ":"
        result += str(dictionary[key])
        result += "\t"
    
    return result


# load functions to function pool
FP = FunctionPool("simple function pool")

F1 = RegisterFunction(square, public=True, always_return=True)
F2 = RegisterFunction(distance, public=True, always_return=True)
F3 = RegisterFunction(black_box_function, public=False, always_return=True)
F4 = RegisterFunction(optimization, public=True, always_return=True)
F5 = RegisterFunction(rev_string, public=True, always_return=True)
F6 = RegisterFunction(cat_string, public=True, always_return=True)
F7 = RegisterFunction(print_dictionary, public=True, always_return=True)

FP.add(F1)  # add the Function object
FP.add(F2)
FP.add(F3)
FP.add(F4)
FP.delete("square")  # delete by name
FP.add(F1)
FP.add(F5)
FP.add(F6)
FP.add(F7)