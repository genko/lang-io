from pypy.lang.io.parserhack import parse, interpret
from pypy.lang.io.model import W_Object, W_Message, W_Number,  W_ImmutableSequence, W_Block
import py.test


def test_object_do():
    inp = '4 do(a := 23)'
    res, space = interpret(inp)
    assert res.slots['a'].value == 23
    assert res.value == 4
    
def test_do_on_map():
    inp = """
    Map do(
        get := method(i, 
            self at(i)
        )
    )
    Map clone atPut("a", 123) atPut("b", 234) atPut("c", 345) get("b")"""
    res, _ = interpret(inp)
    assert isinstance(res, W_Number)
    assert res.value == 234
    
def test_object_do_multiple_slots():
    inp = 'Object do(a := 23; b := method(a + 5); a := 1); Object b'
    res, space = interpret(inp)
    assert res.value == 6
    assert space.w_object.slots['a'].value == 1
    
def test_object_anon_slot():
    inp = 'Object getSlot("+")("foo")'
    res, space = interpret(inp)
    assert res.value == 'foo'

def test_object_has_slot():
    inp = 'Object hasSlot("foo")'
    res, space = interpret(inp)
    assert res is space.w_false
    
    inp2 = 'Object hasSlot("clone")'
    res, space = interpret(inp2)
    assert res is space.w_true
        
def test_object_question_mark_simple():
    inp = 'Object do(a := 1); Object ?a'
    res, space = interpret(inp)
    assert res is not space.w_nil
    assert res.value == 1
    
    inp2 = 'Object ?a'
    res, space = interpret(inp2)
    assert res is space.w_nil

def test_object_message():
    inp = 'message(foo)'
    res, space = interpret(inp)
    assert isinstance(res, W_Message)
    assert res.name == 'foo'
    
def test_object_substract():
    inp = '-1'
    res, space = interpret(inp)
    assert res.value == -1
    
    inp = '-"a"'
    py.test.raises(Exception, "interpret(inp)")
    
def test_object_for():
   inp = """a:= list();
   for(x, 0, 10, 3, a append(x));
   a"""
   res, space = interpret(inp)
   
   assert len(res.items) == 4
   results = [t.value for t in res.items]
   results == [0, 3, 6, 9]
   
def test_improved_object_for():
    
    inp = """a:= list();
    x := 2
    y := 11
    for(x, 0, y - 1, x + 1, a append(x));
    a"""
    res, space = interpret(inp)

    assert len(res.items) == 4
    results = [t.value for t in res.items]
    results == [0, 3, 6, 9]
    
def test_object_for_returns_nil():
    inp = """for(x, 1, 2, nil)"""
    res, space = interpret(inp)
    assert res == space.w_nil
       
def test_object_leaks():
    inp = """a:= list();
    for(x, 0, 10, 3, a append(x));
    x"""
    res, _ = interpret(inp)

    assert res.value == 9
    
def test_object_append_proto():
    inp = """a := Object clone
    b := Object clone
    a appendProto(b)"""
    res, space = interpret(inp)
    assert res.protos == [space.w_object, space.w_lobby.slots['b']]
    
def test_object_doMessage():
    inp = """m := message(asNumber + 123)
    1 doMessage(m)"""
    res, space = interpret(inp)
    
    assert res.value == 124
    
    
def test_object_doMessage_optional_context():
    inp = """m := message(asNumber + 123)
    1 doMessage(m, 2)"""
    res, space = interpret(inp)
    
    assert res.value == 125
    
def test_object_break():
    inp = """for(x, 7, 1000, break)
    x
    """
    res, _ = interpret(inp)
    assert res.value == 7   
    
def test_object_break_return_value():
    inp = """for(x, 7, 1000, break(-1))
    """
    res, _ = interpret(inp)
    assert res.value == -1
    
def test_object_continue():
    inp = """a := list()
    for(x, 1, 10, continue; a append(x))
    """
    res, space = interpret(inp)
    assert space.w_lobby.slots['x'].value == 10
    assert len(space.w_lobby.slots['a'].items) == 0
    
def test_object_return():
    inp = """x := method(y, return)
    x(99)"""
    res, space = interpret(inp)
    assert res == space.w_nil

def test_object_return2():    
    inp = """x := method(y, return; 666)
    x(99)"""
    res, space = interpret(inp)
    assert res.value == 666
    
def test_object_return_value():
    inp = """x := method(y, return 42)
    x(99)"""
    res, space = interpret(inp)
    assert res.value == 42

def test_object_return_value2():    
    inp = """x := method(y, return(1024); 666)
    x(99)"""
    res, space = interpret(inp)
    assert res.value == 1024

def test_object_if():
    inp = """a := list()
    for(i, 1, 10, 
        if(i == 3, continue)
        a append(i))
    a
    """
    res, space = interpret(inp)
    values = [x.value for x in space.w_lobby.slots['a'].items]
    assert values == [1, 2, 4, 5, 6, 7, 8, 9, 10]

def test_object_if2():
    inp = """if(false, 1, 2)"""
    res, _ = interpret(inp)
    assert res.value == 2
    
    inp = """if(true, 1, 2)"""
    res, _ = interpret(inp)
    assert res.value == 1
    
def test_object_if3():
    inp = 'if(true)'
    res, space = interpret(inp)
    assert res is space.w_true
    
    inp = 'if(false)'
    res, space = interpret(inp)
    assert res is space.w_false
    
def test_object_stopStatus():
    inp = 'stopStatus'
    res, space = interpret(inp)
    assert res is space.w_normal
    
    inp = 'stopStatus(break)'
    res, space = interpret(inp)
    assert res is space.w_break
    
    inp = 'stopStatus(continue)'
    res, space = interpret(inp)
    assert res is space.w_continue
    
    inp = 'stopStatus(return 42)'
    res, space = interpret(inp)
    assert res is space.w_return
    
def test_set_slot_with_type():
    inp = """a := Object clone
    setSlotWithType("foo", a)
    """
    res, space = interpret(inp)
    assert isinstance(res.slots['type'], W_ImmutableSequence)
    assert res.slots['type'].value == 'foo'
    assert space.w_lobby.slots['foo'] == res
    
def test_doString():
    inp = """doString("1")"""
    res, space = interpret(inp)
    assert res.value == 1

def test_doString_method():
    inp = """
    doString("method(" .. "foo" .. " = call evalArgAt(0); self)")"""
    res, space = interpret(inp)
    print res
    assert isinstance(res, W_Block)
def test_doString_method2():
    py.test.skip()
    inp = """
    foo := 234
    name := "foo"
    setSlot("set" .. name asCapitalized,
		doString("method(" .. name .. " = call evalArgAt(0); self)"))
    setFoo(1)"""
    res, space = interpret(inp)
    assert res.slots['foo'].value == 1
def test_object_update_slot():
    inp = """
    a := 3
    a = 5
    """
    res, space = interpret(inp)
    assert res.value == 5
    assert space.w_lobby.slots['a'].value == 5
def test_object_update_slot_raises():
    inp = 'qwer = 23'
    py.test.raises(Exception, 'interpret(inp)')
    
def test_object_write():
    inp = """
    p := Object clone do(
        print := method(
            self printed := true
        )
    )
    a := p clone
    b := p clone
    write(a, b)
    """
    res, space = interpret(inp)
    assert res is space.w_nil
    assert space.w_lobby.slots['a'].slots['printed'] is space.w_true
    assert space.w_lobby.slots['b'].slots['printed'] is space.w_true