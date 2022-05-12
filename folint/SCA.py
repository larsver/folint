# SCA.py
import sys
import argparse
import time
from fileinput import filename
from pprint import pprint
from inspect import getmembers
from types import FunctionType
from textx import get_location

from .ast_engine.Parse import IDP
from .ast_engine.utils import IDPZ3Error

def attributes(obj):
    """return attributes of given object"""
    disallowed_names = {
      name for name, value in getmembers(type(obj))
        if isinstance(value, FunctionType)}
    return {
      name: getattr(obj, name) for name in dir(obj)
        if name[0] != '_' and name not in disallowed_names and hasattr(obj, name)}
    
def output(lijst,soort):
    """ Output of error/warning strings in format 'warning/error: line .. - colStart .. - colEnd=> message' """
    print(f"-- {soort} : aantal = {len(lijst)}")
    for i in lijst:
        location = get_location(i[0])
        if hasattr(i[0], 'name'):
            colEnd = location['col'] + len(i[0].name)
        elif hasattr(i[0], 'annotations') and i[0].annotations is not None:
            colEnd = location['col'] + len(i[0].annotations['reading'])
        else:
            colEnd = location['col']
        if argfilename :
            print(f"{filename}: {i[2]}: line {location['line']} - colStart {location['col']} - colEnd {colEnd} => {i[1]}")
        else:
            print(f"{i[2]}: line {location['line']} - colStart {location['col']} - colEnd {colEnd} => {i[1]}")

def doe_de_check(A):
    fouten = []
    A.SCA_Check(fouten)
    warnings = []
    errors = []
    for i in fouten:            #splits warning en errors
        if i[2] == "Warning":
            warnings.append(i)
        else :
            errors.append(i)
    output(errors,"Error")      #output errors
    output(warnings,"Warning")  #output warnings

def sca(idp):
    print("\n---------- Vocabulary Check ----------")
    for v in idp.vocabularies:      #check all vocabularies
        print("-----",v)
        V = idp.get_blocks(v)       #get vocabulary block
        doe_de_check(V[0])          #check
    print("\n---------- Structure Check ----------")
    for s in idp.structures:        #check all structures
        print("-----",s)
        V = idp.get_blocks(s)       #get structure block
        doe_de_check(V[0])          #check
    print("\n---------- Theory Check ----------")
    for t in idp.theories:          #check all theories
        print("-----",t)
        T = idp.get_blocks(t)       #get theory block
        doe_de_check(T[0])          #check
    print("\n---------- Procedure Check ----------")
    for p in idp.procedures:        #check all procedures
        print("-----",p)
        P = idp.get_blocks(p)       #get procedure block
        doe_de_check(P[0])          #check
    

def main():
    parser = argparse.ArgumentParser(description='SCA')
    parser.add_argument('FILE', help='path to the .idp file', type=argparse.FileType('r'))
    parser.add_argument('--no-timing',
                        help='don\'t display timing information',
                        dest='timing', action='store_false',
                        default=True)
    parser.add_argument('--print-AST',
                        help='gives the AST as output',
                        dest='AST', action='store_true',
                        default=False)
    parser.add_argument('--Add-filename',
                        help='Add filename to warning/error output',
                        dest='filename', action='store_true',
                        default=False)
    args = parser.parse_args()

    start_time = time.time()
    try:
        global filename
        global argfilename
        filename = sys.argv[1]
        argfilename = args.filename
        if sys.argv[1].endswith(".idp"):
            idp = IDP.from_file(sys.argv[1])    #parse idp file to AST
            if args.AST:
                idp.printAST(0)                  #print AST van file
            sca(idp)                            #doe SCA
        else:
            print("Expected an .idp file")
    except IDPZ3Error as e1:
        res1 = e1.args[0].split(': ', 1)
        res = res1[0].split()
        print("\n---------- Syntax Error ----------")
        if args.filename :
            print(f"{filename}: {res[0]}: line {res[3].strip(',')} - colStart {res[5].strip(':')} - colEnd {res[5].strip(':')} => {res1[1]}")
        else:
            print(f"{res[0]}: line {res[3].strip(',')} - colStart {res[5].strip(':')} - colEnd {res[5].strip(':')} => {res1[1]}")
    except KeyError as e2:
        # print(e2)
        # pprint(attributes(e2))
        print("KeyError ERROR!!!")
        if args.filename :
            print(f"{filename}: Error: line {0} - colStart {0} - colEnd {0} => Key Error {e2}")
        else :
            print(f"Error: line {0} - colStart {0} - colEnd {0} => Key Error {e2}")
    except Exception as e:
        print("\n---------- Syntax Error ----------")
        # print(e)
        if args.filename :
            print(f"{filename}: Error: line {e.line} - colStart {e.col} - colEnd {e.col} => {e.args}")
        else :
            print(f"Error: line {e.line} - colStart {e.col} - colEnd {e.col} => {e.args}")

    if args.timing:
        print(f"\nElapsed time: {format(time.time() - start_time)} seconds")

if __name__ == "__main__":
    main()
