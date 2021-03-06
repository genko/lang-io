from io.interpreter import parse, interpret
from io.model import W_Object, W_Message, W_Number, W_ImmutableSequence

def test_append():
    inp = '"lo" .. "rem"'
    res, space = interpret(inp)
    assert res.value == 'lorem'

def test_append_returns_copy():
    inp = """
    a := "lo"
    b := a .. ""
    """
    res, space = interpret(inp)
    assert space.w_lobby.slots['a'] is not space.w_lobby.slots['b']

def test_sequence_as_capitalized():
    inp = '"asdf qerttz" asCapitalized'
    res, space = interpret(inp)
    assert res.value == "Asdf qerttz"

    inp = '"fooBar" asCapitalized'
    res, space = interpret(inp)
    assert res.value == "FooBar"
