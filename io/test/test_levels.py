import py
from io.parser import parse, IoParser
from io.model import W_Message, W_Number
from io.levels import Levels, Level, IoException
from io.objspace import ObjSpace

space = ObjSpace()

# Helper methods
def mock_message(name=None, arguments=None, next=None):
    if arguments is None:
        arguments = []
    if name is None:
        name = 'mock_message'
    return W_Message(space, name, arguments, next)

def mock_level(level_type=None, message=None, precedence=None):
    if level_type is None:
        level_type = Levels.NEW
    if message is None:
        message = mock_message()
    if precedence is None:
        precedence = Levels.IO_OP_MAX_LEVEL
    return Level(message, level_type, precedence)

# Tests for Levels
def test_creating_levels():
    l = Levels(space, mock_message())
    assert l.operator_table == \
                        space.w_core.slots['OperatorTable'].slots['operators']
    assert l.assign_operator_table == \
                   space.w_core.slots['OperatorTable'].slots['assignOperators']
                   
def test_current_level_on_creation():
    l = Levels(space, mock_message())
    assert 1 == l.current_level_precedence
    # XXX check the level on init
    #level = l.current_level()

def test_current_level():
    l = Levels(space, mock_message())
    m = mock_level(precedence=1234)
    l.stack.append(m)
    assert l.current_level() is m
    l.stack.insert(0, mock_level())
    assert l.current_level() is m

def test_current_level_empty_stack():
    l = Levels(space, mock_message())
    l.stack = []
    assert l.current_level() is None
    
def test_levels__pop_down_to():
    l = Levels(space, mock_message())
    l.current_level_precedence = 99
    l.stack = []
    l.stack.append(mock_level(level_type=Levels.NEW, precedence=-1))
    l.stack.append(mock_level(level_type=Levels.ARG, precedence=123))
    l.stack.append(mock_level(level_type=Levels.NEW, precedence=95))
    l.stack.append(mock_level(level_type=Levels.NEW, precedence=96))
    print l.stack
    l._pop_down_to(97)
    assert l.current_level_precedence == 97
    assert len(l.stack) == 2
    
def test_levels__is_assign_operator():
    l = Levels(space, mock_message())
    assert l._is_assign_operator(mock_message(":=")) == True
    assert l._is_assign_operator(mock_message("+")) == False
    assert l._is_assign_operator(mock_message("blah")) == False
    
def test_levels__level_for_op_with_op():
    m = mock_message(name='+')
    levels = Levels(space, m)
    assert levels._level_for_op(m) == 3
    
def test_levels__level_for_op_with_non_op():
    m = mock_message(name='lala')
    levels = Levels(space, m)
    assert levels._level_for_op(m) == -1
    
def test_levels__level_for_op_with_negative_precedence():
    m = mock_message(name='+')
    levels = Levels(space, m)
    levels.operator_table.at_put(space.newsequence('+'), W_Number(space, -123))
    py.test.raises(IoException, 'levels._level_for_op(m)')

def test_levels_next_message_for_op_with_nonnumeric_precedence():
    m = mock_message(name='+')
    levels = Levels(space, m)
    levels.operator_table.at_put(space.newsequence('+'), space.w_object.clone())
    py.test.raises(IoException, 'levels._level_for_op(m)')
    
def test_levels_next_message():
    l = Levels(space, mock_message())
    for x in xrange(3):
        l.stack.append(mock_level())
    l.next_message()
    assert len(l.stack) == 0
    
def test_levels__name_for_assign_operator():
    m = mock_message(name=':=')
    slot = mock_message(name="foo")
    l = Levels(space, m)
    assert l._name_for_assign_operator(m, slot).value == 'setSlot'

def test_levels__name_for_assign_operator_with_type():
    m = mock_message(name=':=')
    slot = mock_message(name="Foo")
    l = Levels(space, m)
    assert l._name_for_assign_operator(m, slot).value == 'setSlotWithType'

def test_levels__name_for_assign_operator_with_non_op():
    m = mock_message(name=':fail=')
    slot = mock_message(name="Foo")
    l = Levels(space, m)
    py.test.raises(IoException, 'l._name_for_assign_operator(m, slot)')

# Tests for Level 
def test_level_init():
    level = mock_level()
    assert level.message == mock_message()
    assert level.precedence == Levels.IO_OP_MAX_LEVEL
    assert level.type == Levels.NEW
    
def test_level_attach_and_replace():
    m = mock_message()
    level = mock_level(level_type=Levels.ARG, message=m)
    m2 = mock_message("argument")
    level.attach_and_replace(m2)
    assert level.type == Levels.ATTACH
    assert level.message is m2
    assert m.arguments[0] is m2
    
def test_level_attach_type_attach():
    level = mock_level(Levels.ATTACH)
    m = mock_message(name='foo')
    level.attach(m)
    assert level.message.next is m
    
def test_level_attach_type_new():
    level = mock_level(Levels.NEW)
    m = mock_message(name='foo')
    level.attach(m)
    assert level.message is m

def test_level_attach_type_arg():
    level = mock_level(Levels.ARG)
    m = mock_message(name='foo')
    level.attach(m)
    assert level.message.arguments[-1] is m
    
def test_level_attach_type_unused():
    level = mock_level(Levels.UNUSED)
    m = mock_message(name='foo')
    level.attach(m)
    assert level.message is not m
    assert level.message.next is not m
    assert m not in level.message.arguments
    
def test_level_finish_removes_anon_message():
    op_message = mock_message('+', [mock_message('', [mock_message('foo')])])
    level = mock_level(level_type=Levels.ATTACH, message=op_message)
    assert level.message.name == '+'
    assert level.message.arguments[0].name == ''
    level.finish()
    assert level.message.name == '+'
    assert len(level.message.arguments) == 1
    assert level.message.arguments[0].name == 'foo'
    
def test_level_finish_keeps_named_messages():
    o_message = mock_message('+', [mock_message('bar', [mock_message('foo')])])
    level = mock_level(level_type=Levels.ATTACH, message=o_message)
    level.finish()
    assert level.message.name == '+'
    assert level.message.arguments[0].name == 'bar'
    
def test_level_name_for_type_attach():
    level = mock_level(Levels.ATTACH)
    assert level.name_for_type() == 'ATTACH'

def test_level_name_for_type_new():
    level = mock_level(Levels.NEW)
    assert level.name_for_type() == 'NEW'

def test_level_name_for_type_arg():
    level = mock_level(Levels.ARG)
    assert level.name_for_type() == 'ARG'

def test_level_name_for_type_unused():
    level = mock_level(Levels.UNUSED)
    assert level.name_for_type() == 'UNUSED'
    