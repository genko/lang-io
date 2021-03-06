import py
from io.parser import parse, IoParser
from io.model import W_Message, W_Number
from io.levels import Levels
from io.objspace import ObjSpace

space = ObjSpace()

def test_operator_shuffling1():
    inp = "a + b"
    res = parse(space, inp)
    res.shuffle()
    # res == a +(b)
    assert res.name == "a"
    plus = res.next
    assert plus.name == "+"
    assert plus.arguments[0].name == "b"

def test_operator_shuffling2():
    inp = 'a +(b)'
    res = parse(space, inp)
    res.shuffle()
    assert res.name == "a"
    plus = res.next
    assert plus.name == "+"
    assert plus.arguments[0].name == "b"

def test_levels_attach_for_non_operator():
    inp = "a"
    res = parse(space, inp)
    l = Levels(space, W_Message(space, "foo", []))
    l.attach(res, [])
    assert l.current_level().message == res
    assert l.current_level().type == Levels.ATTACH
    assert l.current_level().precedence == Levels.IO_OP_MAX_LEVEL

def test_levels_stack_on_init_has_one_level():
    l = Levels(space, W_Message(space, "nil", []))
    assert len(l.stack) == 1
    assert l.stack[0].message == None
    assert l.stack[0].type == Levels.NEW
    assert l.stack[0].precedence == Levels.IO_OP_MAX_LEVEL

def test_foo():
    inp = "foo bar baz"
    res = parse(space, inp)
    print res.name
    res.shuffle()

def test_levels_current_level():
    l = Levels(space, W_Message(space, "nil", []))
    l.stack.insert(0, 1)
    assert l.current_level() == l.stack[-1]

def test_levels_attach_for_eol():
    inp = "a ; b"
    res = parse(space, inp)
    res.shuffle()
    assert res.name == 'a'
    assert res.next.name == ';'
    assert res.next.next.name == 'b'

def test_shuffle_method_body():
    inp = """Object do(
      /*doc Object inlineMethod
      Creates a method which is executed directly in a receiver (no Locals object is created).
      <br/>
      <pre>
      Io> m := inlineMethod(x := x*2)
      Io> x := 1
      ==> 1
      Io> m
      ==> 2
      Io> m
      ==> 4
      Io> m
      ==> 8
      </pre>
      */
    	inlineMethod := method(call message argAt(0) setIsActivatable(true))
    )"""
    res = parse(space, inp)
    print res

def test_assign_operator_shuffling():
    inp = "a  = b"
    res = parse(space, inp)
    res.shuffle()
    assert res.name == 'updateSlot'
    assert len(res.arguments) == 2
    assert res.next == None

def test_assign_operator_shuffling2():
    inp = 'a := b'
    res = parse(space, inp)
    res.shuffle()
    assert res.name == 'setSlot'
    assert len(res.arguments) == 2
    assert res.next == None

def test_assign_operator_shuffling3():
    inp = 'a ::= b'
    res = parse(space, inp)
    res.shuffle()
    assert res.name == 'newSlot'
    assert len(res.arguments) == 2
