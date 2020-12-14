# Function service

import inspect
import logging

FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO, filename="trace.log")
#logger = logging.getLogger("FunctionService")
logger = logging.getLogger()

class Function(object):
    def __init__(self, function, name, public=True, doc='', always_return=True, allow_shared=False):
        self.function = function
        self.name = name
        self.public = public
        self.doc = doc # additional documentations, not docstring
        self.always_return = always_return
        self.allow_shared = allow_shared  # one Function can be put into different FunctionPool (or not)
        self.attached_pools = []  # attached FunctionPool(s), always be empty if allow_shared is false
        print("[FunctionService] Function [" + str(self.name) + "] registered.")
        logger.info("[FunctionService] Function [" + str(self.name) + "] registered.")

    def __call__(self, *args):  # no security checks here
        if self.always_return:
            return self.function(*args)
        else:
            self.function(*args)

    def get_name(self):
        return self.name

    def get_source(self):
        return self.__str__()

    def get_attached_pools(self):
        return self.attached_pools

    def allow_shared(self):
        return self.allow_shared

    def is_public(self):
        return self.public

    def update_doc(self, doc):
        self.doc = doc

    def examine(self):
        print("****************************************")
        print("Function name: " + str(self.name()))
        print("Function implementation: ")
        print(self.get_source())
        print("Always return: " + str(self.always_return))
        print("Allow shared: " + str(self.allow_shared))
        print("Attached FunctionPool(s): ")
        print(self.attached_pools)
        print("****************************************")

    def __str__(self):
        return inspect.getsource(self.function)


class FunctionPool(object):
    def __init__(self, name, public=True):
        self.name = name  # Notice: cannot be changed
        self.functions = {}
        self.activation_status = {} # active or not
        self.running_status = {} # running or not
        self.public = public

    def add(self, F, is_active=True):
        # check the type
        if not isinstance(F, Function):
            print("[FunctionPoolService]" + self.name + "[ADD] Only a registered Function can be added.")
            logger.warning("[FunctionPoolService]" + self.name + "[ADD] Only a registered Function can be added.")
            return False
        else:
            F_name = F.get_name()  # get the name of Function

        # check if it can be shared
        if (not F.allow_shared) and (F.get_attached_pools()):
            print("[FunctionPoolServive]" + self.name + "[ADD] Function cannot be shared, occupied by another FunctionPool.")
            logger.warning("[FunctionPoolServive]" + self.name + "[ADD] Function cannot be shared, occupied by another FunctionPool.")
            return False

        # check if it already exist
        if self.contains(F_name):
            print("[FunctionPoolService]" + self.name + "[ADD] Function [" + F_name + "] has been occupied.")
            logger.warning("[FunctionPoolService]" + self.name + "[ADD] Function [" + F_name + "] has been occupied.")
            return False
        
        # Update info in FunctionPool
        self.functions.update({str(F_name): F})
        self.activation_status.update({str(F_name): is_active})
        self.running_status.update({str(F_name): False}) # not running now

        # Update info in Function itself
        # That's why we cannot change the name of FunctionPool... I don't want to implement this
        # Pass by reference, side effects
        F.get_attached_pools().append(self.name)  # notice, self.name is the name of FunctionPool

        print("[FunctionPoolService]" + self.name + "[ADD] Function [" + F_name + "] added.")
        logger.info("[FunctionPoolService]" + self.name + "[ADD] Function [" + F_name + "] added.")
        return True

    def delete(self, name):
        if not self.contains(name):
            print("[FunctionPoolService]" + self.name + "[DELETE] Cannot find function [" + str(name) + "].")
            logger.warning("[FunctionPoolService]" + self.name + "[DELETE] Cannot find function [" + str(name) + "].")
            return False

        # Update info in Function itself (first)
        # Because we plan to delete it later
        F = self.functions[name]
        # Pass by reference, side effects
        F.get_attached_pools().remove(self.name) # notice, self.name is the name of FunctionPool

        # Update info in FunctionPool
        self.functions.pop(name)
        self.activation_status.pop(name)
        self.running_status.pop(name)

        print("[FunctionPoolService]" + self.name + "[DELETE] Function [" + name + "] deleted.")
        logger.info("[FunctionPoolService]" + self.name + "[DELETE] Function [" + name + "] deleted.")
        return True

    def contains(self, name):
        return (name in self.functions)

    def is_active(self, name):
        if not self.contains(name):
            print("[FunctionPoolService]" + self.name + "[IS_ACTIVE] Cannot find function [" + str(name) + "].")
            logger.warning("[FunctionPoolService]" + self.name + "[IS_ACTIVE] Cannot find function [" + str(name) + "].")
            return False  # Notice, False also means not existed
        
        return self.activation_status[name]

    def activate(self, name):  # callable
        if not self.contains(name):
            print("[FunctionPoolService]" + self.name + "[ACTIVATE] Cannot find function [" + str(name) + "].")
            logger.warning("[FunctionPoolService]" + self.name + "[ACTIVATE] Cannot find function [" + str(name) + "].")
            return False
        
        self.activation_status.update({name: True})
        print("[FunctionPoolService]" + self.name + "[ACTIVATE] Function [" + str(name) + "] is activated.")
        logger.info("[FunctionPoolService]" + self.name + "[ACTIVATE] Function [" + str(name) + "] is activated.")

        return True

    def deactivate(self, name):  # not callable
        if not self.contains(name):
            print("[FunctionPoolService]" + self.name + "[DEACTIVATE] Cannot find function [" + str(name) + "].")
            logger.warning("[FunctionPoolService]" + self.name + "[DEACTIVATE] Cannot find function [" + str(name) + "].")
            return False
        
        self.activation_status.update({name: False})
        print("[FunctionPoolService]" + self.name + "[DEACTIVATE] Function [" + str(name) + "] is deactivated.")
        logger.info("[FunctionPoolService]" + self.name + "[DEACTIVATE] Function [" + str(name) + "] is deactivated.")

        return True

    # under development
    def is_running(self, name):
        if not self.contains(name):
            print("[FunctionPoolService]" + self.name + "[IS_RUNNING] Cannot find function [" + str(name) + "].")
            logger.warning("[FunctionPoolService]" + self.name + "[IS_RUNNING] Cannot find function [" + str(name) + "].")
            return False

        return self.running_status[name]
    
    def call(self, name, *args):
        if not self.contains(name):
            print("[FunctionPoolService]" + self.name + "[CALL] Cannot find function [" + str(name) + "].")
            logger.warning("[FunctionPoolService]" + self.name + "[CALL] Cannot find function [" + str(name) + "].")
            return "Cannot find function [" + str(name) + "]."  # inform the client
        
        if not self.is_active(name):
            # Notice that we plan to return the error message to the client
            print("[FunctionPoolService]" + self.name + "[CALL] The function [" + str(name) + "] is not activated.")
            logger.warning("[FunctionPoolService]" + self.name + "[CALL] The function [" + str(name) + "] is not activated.")
            return "[CALL] The function [" + str(name) + "] is not activated."

        if self.is_running(name):
            # Keep it simple, please
            print("[FunctionPoolService]" + self.name + "[CALL] The function [" + str(name) + "] is running by other process, be patient.")
            logger.info("[FunctionPoolService]" + self.name + "[CALL] The function [" + str(name) + "] is running by other process, be patient.")
            return "[CALL] The function [" + str(name) + "] is running by other process, be patient."
            
        if self.functions[name].always_return:
            args_string = ""
            for arg in args:
                args_string += str(arg)
            print("[FunctionPoolService]" + self.name + "[CALL] " + name + "(" + args_string + ")")
            logger.info("[FunctionPoolService]" + self.name + "[CALL] " + name + "(" + args_string + ")")
            
            return self.functions[name].__call__(*args)
        else:
            self.functions[name].__call__(*args)
            print("[FunctionPoolService]" + self.name + "[CALL] Finished.")
            logger.info("[FunctionPoolService]" + self.name + "[CALL] Finished.")
            return "[CALL] Finished"
        
    def examine(self, detailed=False, return_msg=False):
        msg = ""
        msg += "########################################\n"
        msg += "FunctionPool name: " + str(self.name) + "\n"

        total_num = 0
        active_num = 0
        running_num = 0

        for f_name in self.functions:
            if detailed:
                msg += "****************************************\n"
                msg += "Function name: " + str(f_name) + "\n"
                msg += "Function active: " + str(self.is_active(f_name)) + "\n"
                msg += "Function running: " + str(self.is_running(f_name)) + "\n"
                msg += "Function implementation:\n"
                if self.functions[f_name].is_public():
                    msg += str(self.functions[f_name]) + "\n"
                else:
                    msg += "\nFunction implementation hidden.\n\n"
                msg += "****************************************\n"
                

            if (self.is_active(f_name)):
                active_num += 1
            if (self.is_running(f_name)):
                running_num += 1
            total_num += 1

        msg += str(total_num) + " function(s) total\n"
        msg += str(active_num) + " function(s) active.\n"
        msg += str(running_num) + " function(s) running.\n"
        msg += "########################################\n"

        if return_msg:
            return msg
        else:
            print(msg)


def RegisterFunction(f, doc='', public=True, always_return=True, allow_shared=False):
    if not inspect.isfunction(f):
        print("We can only register a function")
        logger.warning("We can only register a function")  # includes lambda functions
        return False
    
    # Before:
    #   def example_function(x, y, z):
    # After:
    #   example_function
    f_name = inspect.getsource(f).split('\n')[0][:-1].split(' ')[1].split('(')[0]

    # doc is additional documents, not docstring
    return Function(f, f_name, public=public, doc=doc, always_return=always_return, allow_shared=allow_shared)
