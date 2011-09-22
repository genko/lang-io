from io.interpreter import parse, interpret

def test_updateSlot_in_self():
    inp = """a := Object clone
    a foo := 5
    a bar := method(foo = 10)
    a bar
    a foo
    """
    res, space = interpret(inp)
    assert res.number_value == 10
    assert space.w_lobby.slots['a'].slots['foo'].number_value == 10

def test_updateSlot_in_locals():
    inp = """a := Object clone
    a foo := 5
    a bar := method(foo := foo; foo = 10)
    a bar
    """
    res, space = interpret(inp)
    assert res.number_value == 10
    assert space.w_lobby.slots['a'].slots['foo'].number_value == 5
