import py
import os
import glob

from io.model import W_Number, parse_literal, W_Message
from io.objspace import ObjSpace

from io.parser import parse

def interpret(code):
    space = ObjSpace()
    load_io_files(space)
    ast = parse(space, code)
    return ast.eval(space, space.w_lobby, space.w_lobby), space

def parse_file(filename, space=None):
    f = file(filename)
    code = f.read()
    f.close()
    # import pdb; pdb.set_trace()
    return parse(space, code)


def extract_name(input):
    re.match(input, '\"(\\"|[^"])+\"')
def load_io_files(space):
    files = glob.glob('io/*.io')
    for f in files:
        parse_file(f, space).eval(space, space.w_lobby, space.w_lobby)


if __name__ == '__main__':
    import sys
    space = ObjSpace()
    # print parse(py.path.local(sys.argv[1]).read(), space)
    print parse(space, sys.argv[1])


