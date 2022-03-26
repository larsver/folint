# __main__.py

import sys
import argparse
import time
from pprint import pprint
from inspect import getmembers
from types import FunctionType
from textx import get_location

from .ast_engine.Parse import IDP
from .ast_engine.utils import IDPZ3Error
# from ast_engine.Parse import IDP
# from ast_engine.utils import IDPZ3Error

#functie return attributes of object
def attributes(obj):
    disallowed_names = {
      name for name, value in getmembers(type(obj))
        if isinstance(value, FunctionType)}
    return {
      name: getattr(obj, name) for name in dir(obj)
        if name[0] != '_' and name not in disallowed_names and hasattr(obj, name)}
#pprint(attributes(obj))

#output errors/warnings vorm = "warning/error: line .. - colStart .. - colEnd=> message"
def output(errors,warnings):
    print(f"-- Errors : aantal = {len(errors)}")
    for i in errors:
        location = get_location(i[0])
        if hasattr(i[0], 'annotations'):
            colEnd = location['col'] + len(i[0].annotations['reading'])
        else :
            colEnd = location['col'] + len(i[0].name)
        # print(f"{i[2]}: line {location['line']} - col {location['col']} => {i[1]}")
        print(f"{i[2]}: line {location['line']} - colStart {location['col']} - colEnd {colEnd} => {i[1]}")
    print(f"-- Warnings : aantal = {len(warnings)}")
    for i in warnings:
        # print(i[0],":",type(i[0]))    
        location = get_location(i[0])
        if hasattr(i[0], 'annotations'):
            colEnd = location['col'] + len(i[0].annotations['reading'])
        else :
            colEnd = location['col'] + len(i[0].name)
        # print(f"{i[2]}: line {location['line']} - col {location['col']} => {i[1]}")
        print(f"{i[2]}: line {location['line']} - colStart {location['col']} - colEnd {colEnd} => {i[1]}")

def doe_de_check(A):
    fouten = []
    A.mijnCheck(fouten)
    warnings = []
    errors = []
    for i in fouten:    #splits warning en errors
        if i[2] == "Warning":
            warnings.append(i)
        else :
            errors.append(i)
    output(errors,warnings)

def sca(idp):
    print(" ")
    print("---------- Theory Check ----------")
    for t in idp.theories:          #check all theories
        print("-----",t)
        T = idp.get_blocks(t)       #get theory block
        doe_de_check(T[0])            #check
    print(" ")
    print("---------- Procedure Check ----------")
    for p in idp.procedures:    #check all procedures
        print("-----",p)
        P = idp.get_blocks(p)   #get block
        doe_de_check(P[0])        #check

def main():
    parser = argparse.ArgumentParser(description='SCA')
    parser.add_argument('FILE', help='path to the .idp file', type=str)
    parser.add_argument('--no-timing',
                        help='don\'t display timing information',
                        dest='timing', action='store_false',
                        default=True)
    parser.add_argument('--print-AST',
                        help='gives the AST as output',
                        dest='AST', action='store_true',
                        default=False)
    args = parser.parse_args()
    # print(args.FILE)
    # print(args.timing)

    start_time = time.time()
    try:
        if sys.argv[1].endswith(".idp"):
            idp = IDP.from_file(sys.argv[1])    #parse idp file to AST
            if args.AST:
                idp.mijnAST(0)                     #print AST van file
            sca(idp)                            #doe SCA
        else:
            print("Expected an .idp file")
    except IDPZ3Error as e1:
        # print(e1)
        # print("args:",e1.args[0],":",type(e1.args[0]))   
        res1 = e1.args[0].split(': ', 1)
        res = res1[0].split()
        print("---------- Syntax Error ----------")
        print(f"{res[0]}: line {res[3].strip(',')} - colStart {res[5].strip(':')} - colEnd {res[5].strip(':')} => {res1[1]}")
    except KeyError as e2:
        print(e2)
        pprint(attributes(e2))
        print(e2.with_traceback)
        print("KeyError ERROR!!!")
    except Exception as e:
        print(e)
        # pprint(attributes(e))
        print("---------- Syntax Error ----------")
        print(f"Error: line {e.line} - colStart {e.col} - colEnd {e.col} => {e.args}")

    if args.timing:
            print("\nElapsed time: {} seconds".format(time.time() - start_time))



if __name__ == "__main__":
    main()