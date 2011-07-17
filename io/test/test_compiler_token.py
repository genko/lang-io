from io.interpreter import interpret
from io.model import W_Object, W_Number
import py

def test_compiler_token_for_number_is_number():
    inp = 'Compiler tokensForString("1")'
    res, space = interpret(inp)
    assert res.list_items[0].slots['character'].number_value == 1
    assert res.list_items[0].slots['line'].number_value == 1
    assert res.list_items[0].slots['type'].value == 'Number'
    assert res.list_items[0].slots['name'].value == "1"
    assert isinstance(res.list_items[0], W_Object)

def test_compiler_token_HexNumber():
    inp = 'Compiler tokensForString("0x1")'
    res, space = interpret(inp)
    assert res.list_items[0].slots['character'].number_value == 3
    assert res.list_items[0].slots['line'].number_value == 1
    assert res.list_items[0].slots['type'].value == 'HexNumber'
    assert res.list_items[0].slots['name'].value == "0x1"
    assert isinstance(res.list_items[0], W_Object)

def test_compiler_token_open_paren():
    inp = 'Compiler tokensForString("()")'
    res, space = interpret(inp)
    assert res.list_items[1].slots['character'].number_value == 1
    assert res.list_items[1].slots['line'].number_value == 1
    assert res.list_items[1].slots['type'].value == 'OpenParen'
    assert res.list_items[1].slots['name'].value == "("
    assert isinstance(res.list_items[1], W_Object)

def test_compiler_token_close_paren():
    inp = 'Compiler tokensForString("()")'
    res, space = interpret(inp)
    assert res.list_items[2].slots['character'].number_value == 2
    assert res.list_items[2].slots['line'].number_value == 1
    assert res.list_items[2].slots['type'].value == 'CloseParen'
    assert res.list_items[2].slots['name'].value == ")"
    assert isinstance(res.list_items[2], W_Object)

def test_compiler_parse_paren_produces_anon_message():
    inp = 'Compiler tokensForString(" ()")'
    res, space = interpret(inp)
    assert res.list_items[0].slots['character'].number_value == 1
    assert res.list_items[0].slots['line'].number_value == 1
    assert res.list_items[0].slots['type'].value == 'Identifier'
    assert res.list_items[0].slots['name'].value == ""
    assert isinstance(res.list_items[0], W_Object)

def test_compiler_parse_paren_produces_anon_message():
    inp = 'Compiler tokensForString("()")'
    res, space = interpret(inp)
    assert res.list_items[0].slots['character'].number_value == 0
    assert res.list_items[0].slots['line'].number_value == 1
    assert isinstance(res.list_items[0], W_Object)

# curlyBraces
def test_compiler_token_open_squareBrackets():
    inp = 'Compiler tokensForString("[]")'
    res, space = interpret(inp)
    assert res.list_items[1].slots['character'].number_value == 1
    assert res.list_items[1].slots['line'].number_value == 1
    assert res.list_items[1].slots['type'].value == 'OpenParen'
    assert res.list_items[1].slots['name'].value == "["
    assert isinstance(res.list_items[1], W_Object)

def test_compiler_token_squareBrackets():
    inp = 'Compiler tokensForString("[]")'
    res, space = interpret(inp)
    assert res.list_items[2].slots['character'].number_value == 2
    assert res.list_items[2].slots['line'].number_value == 1
    assert res.list_items[2].slots['type'].value == 'CloseParen'
    assert res.list_items[2].slots['name'].value == "]"
    assert isinstance(res.list_items[2], W_Object)

def test_compiler_parse_paren_produces_squareBrackets_message():
    inp = 'Compiler tokensForString("[]")'
    res, space = interpret(inp)
    assert res.list_items[0].slots['character'].number_value == 0
    assert res.list_items[0].slots['line'].number_value == 1
    assert res.list_items[0].slots['type'].value == 'Identifier'
    assert res.list_items[0].slots['name'].value == "squareBrackets"
    assert isinstance(res.list_items[0], W_Object)

# curlyBrackets
def test_compiler_token_open_curlyBrackets():
    inp = 'Compiler tokensForString("{}")'
    res, space = interpret(inp)
    assert res.list_items[1].slots['character'].number_value == 1
    assert res.list_items[1].slots['line'].number_value == 1
    assert res.list_items[1].slots['type'].value == 'OpenParen'
    assert res.list_items[1].slots['name'].value == "{"
    assert isinstance(res.list_items[1], W_Object)

def test_compiler_token_curlyBrackets():
    inp = 'Compiler tokensForString("{}")'
    res, space = interpret(inp)
    assert res.list_items[2].slots['character'].number_value == 2
    assert res.list_items[2].slots['line'].number_value == 1
    assert res.list_items[2].slots['type'].value == 'CloseParen'
    assert res.list_items[2].slots['name'].value == "}"
    assert isinstance(res.list_items[2], W_Object)

def test_compiler_parse_paren_produces_curlyBrackets_message():
    inp = 'Compiler tokensForString("{}")'
    res, space = interpret(inp)
    assert res.list_items[0].slots['character'].number_value == 0
    assert res.list_items[0].slots['line'].number_value == 1
    assert res.list_items[0].slots['type'].value == 'Identifier'
    assert res.list_items[0].slots['name'].value == "curlyBrackets"
    assert isinstance(res.list_items[0], W_Object)

def test_compiler_identifier_token():
    inp = 'Compiler tokensForString("foo")'
    res, space = interpret(inp)
    assert res.list_items[0].slots['character'].number_value == 3
    assert res.list_items[0].slots['line'].number_value == 1
    assert res.list_items[0].slots['type'].value == 'Identifier'
    assert res.list_items[0].slots['name'].value == 'foo'
    assert isinstance(res.list_items[0], W_Object)

def test_compiler_terminator_token_for_newline():
    inp = """Compiler tokensForString("\n")"""
    res, space = interpret(inp)
    # assert res.items[0].slots['character'].value == 1
    # assert res.items[0].slots['line'].value == 1
    assert res.list_items[0].slots['type'].value == 'Terminator'
    assert res.list_items[0].slots['name'].value == ";"
    assert isinstance(res.list_items[0], W_Object)


def test_compiler_terminator_token():
    inp = 'Compiler tokensForString(";")'
    res, space = interpret(inp)
    assert res.list_items[0].slots['character'].number_value == 1
    assert res.list_items[0].slots['line'].number_value == 1
    assert res.list_items[0].slots['type'].value == 'Terminator'
    assert res.list_items[0].slots['name'].value == ";"
    assert isinstance(res.list_items[0], W_Object)

def test_compiler_comma_token():
    inp = 'Compiler tokensForString("(1,2)")'
    res, space = interpret(inp)
    assert res.list_items[3].slots['character'].number_value == 3
    assert res.list_items[3].slots['line'].number_value == 1
    assert res.list_items[3].slots['type'].value == 'Comma'
    assert res.list_items[3].slots['name'].value == ","
    assert isinstance(res.list_items[3], W_Object)

@py.test.mark.xfail
def test_compiler_triquote_token():
    inp = 'Compiler tokensForString("\"\"\"asdf\"\"\"")'
    res, space = interpret(inp)
    assert res.list_items[0].slots['type'].value == 'TriQuote'
    assert res.list_items[0].slots['name'].value == "\"\"\"asdf\"\"\""
    assert isinstance(res.list_items[0], W_Object)

@py.test.mark.xfail
def test_compiler_monoquote_token():
    inp = 'Compiler tokensForString("\\\"lorem\\\"")'
    res, space = interpret(inp)
    assert res.list_items[0].slots['name'].value == "\"lorem\""
    assert res.list_items[0].slots['type'].value == 'MonoQuote'
    assert isinstance(res.list_items[0], W_Object)

def test_compiler_comment_token():
    py.test.skip("These Tokens are ignored by the lexer")
    inp = 'Compiler tokensForString("xxx")'
    res, space = interpret(inp)
    assert res.list_items[0].slots['type'].value == 'Comment'
    assert res.list_items[0].slots['name'].value == "??"
    assert isinstance(res.list_items[0], space.x)
