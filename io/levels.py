import io

def _create_assign_operator_table(space):
    ass_op_table = space.w_map.clone()
    ass_op_table.at_put(':=', space.newsequence('setSlot'))
    ass_op_table.at_put('=', space.newsequence('updateSlot'))
    ass_op_table.at_put('::=', space.newsequence('newSlot'))
    return ass_op_table

def _create_operator_table(space):
    # print "_create_operator_table called"
    table = {"@": 0, "@@": 0, "?": 0, "**": 1, "*": 2, "/": 2, "%": 2,
    "+": 3, "-": 3, "<<": 4, ">>": 4, ">": 5, "<": 5, "<=": 5, ">=": 5,
    "==": 6, "!=": 6, "&": 7, "^": 8, "|": 9, "and": 10, "&&": 10,
    "or": 11, "||": 11, "..": 12, "+=": 13, "-=": 13, "*=": 13, "/=": 13,
    "%=": 13, "&=": 13, "^=": 13, "|=": 13, "<<=": 13, ">>=": 13,
    "return": 14}
    op_table = space.w_map.clone()
    for key in table:
        op_table.at_put(key, io.model.W_Number(space, table[key]))
    return op_table

class Levels(object):
    NEW = 0
    ATTACH = 1
    ARG = 2
    UNUSED = 3
    IO_OP_MAX_LEVEL = 32

    def __init__(self, space, w_message):
        self.space = space
        if 'OperatorTable' not in w_message.slots:
            # print "OperatorTable not in message slots"
            if 'OperatorTable' not in space.w_core.slots:
                # print "OperatorTable not in Core slots"
                # create a new one in state.w_core
                operator_table = space.w_object.clone()
                space.w_core.slots['OperatorTable'] = operator_table
                operator_table.slots['precedenceLevelCount'] = io.model.W_Number(space, Levels.IO_OP_MAX_LEVEL)
            else:
                operator_table = space.w_core.slots['OperatorTable']
        else:
            operator_table = w_message.slots['OperatorTable']
        self.operator_table = self._get_op_table(operator_table, 'operators', _create_operator_table)
        self.assign_operator_table = self._get_op_table(operator_table, 'assignOperators', _create_assign_operator_table)
        self.reset()

    def reset(self):
        self.pool = [Level() for i in range(Levels.IO_OP_MAX_LEVEL)]
        self.current_level_precedence = 1

        level = self.pool[0]
        level.message = None
        level.precedence = Levels.IO_OP_MAX_LEVEL

        self.stack = [level]

    def _get_op_table(self, operator_table, slot_name, callback=None):
        if slot_name in operator_table.slots and isinstance(operator_table.slots[slot_name], io.model.W_Map):
            return operator_table.slots[slot_name]

        else:
            # Ref: IoMessage_opShuffle.c line 155
            # Not strictly correct as if the message has its own empty
            # OperatorTable slot, we'll create one for it instead of using
            # Core Message OperatorTable operators. Oh well.
            result = callback(self.space)
            operator_table.slots[slot_name] = result
            return result

    def current_level(self):
        if len(self.stack) == 0:
            return None
        return self.stack[-1]

    def attach(self, w_message, expressions):
        name = w_message.name
        precedence = self._level_for_op(w_message)
        n_args = len(w_message.arguments)

        if self._is_assign_operator(w_message):
            current_level = self.current_level()
            attaching = current_level.message
            self._check_attaching(attaching, w_message)
            # a := b ;
            copy_of_message = io.model.W_Message(self.space, '"%s"' % attaching.name, [])
            # copy_of_message.update_source_location(attaching)
            # a := b ;  ->  a("a") := b ;
            attaching.arguments.append(copy_of_message)


            attaching.name = self._name_for_assign_operator(w_message, copy_of_message)
            current_level.type = Levels.ATTACH

            if n_args > 0: #setSlot("a") :=(b c) d e ;
                # b c
                arg = w_message.arguments[0]
                if w_message.next is None or w_message.next.name == ';':
                    attaching.arguments.append(arg)
                else:
                    # ()
                    foo = io.model.W_Message(self.space, '', [])
                    # XXX IoMessage_rawCopySourceLocation(foo, attaching);
                    # ()  ->  (b c)
                    foo.arguments.append(arg)
                    # (b c)  ->  (b c) d e ;
                    foo.next = w_message
                    # setSlot("a") :=(b c) d e ;  ->  setSlot("a", (b c) d e ;) :=(b c) d e ;
                    attaching.arguments.append(foo)
            else:
                # setSlot("a") := b ;
                #setSlot("a") := or setSlot("a") := ;
                if w_message.next is None or w_message.name == ';':
                    # XXX raise an error
                    # print "compile error: %s must be followed by a value." % w_message.name
                    return
                # setSlot("a") := b c ;  ->  setSlot("a", b c ;) := b c ;
                attaching.arguments.append(w_message.next)

            # process the value (b c d) later  (setSlot("a", b c d) := b c d ;)
            if w_message.next is not None and not w_message.next.name == ';':
                expressions.append(w_message.next)
            last = w_message
            while last.next is not None and not last.next.name == ';':
                last = last.next

            attaching.next = last.next

            # Continue processing in IoMessage_opShuffle loop
            w_message.next = last.next

            if last is not w_message:
                last.next = None

            # make sure b in 1 := b gets executed
            attaching.cached_result = None
        elif w_message.name == ';':
            # print "message name is ;"
            self._pop_down_to(Levels.IO_OP_MAX_LEVEL-1, expressions)
            self.current_level().attach_and_replace(w_message)
        elif precedence != -1:
          if n_args > 0:
                # move arguments off to their own message to make () after operators behave like Cs grouping ()
                brackets = io.model.W_Message(self.space, "", [])
                # XXX IoMessage_rawCopySourceLocation(brackets, msg);
                brackets.arguments = w_message.arguments
                w_message.arguments = []
                # Insert the brackets message between msg and its next message
                brackets.next = w_message.next
                w_message.next = brackets
          self._pop_down_to(precedence, expressions)
          self._attach_to_top_and_push(w_message, precedence)
        else:
          self.current_level().attach_and_replace(w_message)

    def _check_attaching(self, attaching, w_message):
        if attaching is None:
            raise IoException("compile error: %s requires a symbol to its \
                                left." % w_message.name)
        if len(attaching.arguments) > 0:
            raise IoException("compile error: The symbol to the left of %s \
                                cannot have arguments." % w_message.name)
        if len(w_message.arguments) > 1:
            raise IoException("compile error: Assign operator(%s) passed \
                                multiple arguments, e.g., a := (b, c)."
                                % w_message.name)

    def _attach_to_top_and_push(self, w_message, precedence):
        top = self.current_level()
        top.attach_and_replace(w_message)
        # XXX Check for overflow of the pool.
        # print 'current_level_precedence is %d' % self.current_level_precedence
        if self.current_level_precedence >= Levels.IO_OP_MAX_LEVEL:
            raise IoException("compile error: Overflowed operator stack. Only \
                    %d levels of operators currently supported."
                    % (Levels.IO_OP_MAX_LEVEL-1))
        self.current_level_precedence +=1
        level = self.pool[self.current_level_precedence]
        level.set_waiting_for_first_arg(w_message, precedence)
        self.stack.append(level)
        # print self.stack

    def _name_for_assign_operator(self, operator, slot):
        name = self.assign_operator_table.at(operator.name)
        if name is not self.space.w_nil and isinstance(name,
                                                io.model.W_ImmutableSequence):
            if operator.name == ":=" and slot.name[0].isupper():
                return "setSlotWithType"
            else:
                return name.value
        else:
            raise IoException("compile error: Value for '%s' in Message \
                    OperatorTable assignOperators is not a symbol. Values in \
                    the OperatorTable assignOperators are symbols which are \
                    the name of the operator." % operator.name)

    def _pop_down_to(self, target_level, expressions):
        level = self.current_level()
        while (level.precedence <= target_level
                    and level.type != Levels.ARG):
            self.stack.pop().finish(expressions)
            self.current_level_precedence -= 1
            level = self.current_level()

    def _is_assign_operator(self, w_message):
        return self.assign_operator_table.has_key(w_message.name)

    def _level_for_op(self, w_message):
        if not self.operator_table.has_key(w_message.name):
            # print "%s not found in the operator_table slots" % w_message.name
            return -1
        operator = self.operator_table.at(w_message.name)
        if isinstance(operator, io.model.W_Number):
            value = operator.number_value
            if value < 0 or value >= Levels.IO_OP_MAX_LEVEL:
                #'XXX Some corresponding exception'#error
                raise IoException("compile error: Precedence for operators \
                    must be between 0 and %d. Precedence was %f."
                    % (Levels.IO_OP_MAX_LEVEL - 1, value))
            return value
        else:
            raise IoException("compile error: Value for '%s' in Message \
                OperatorTable operators is not a number. Values in the \
                OperatorTable operators are numbers which indicate the \
                precedence of the operator." % w_message.name)

    def next_message(self, expressions):
        while len(self.stack) > 0:
            level = self.stack.pop()
            level.finish(expressions)
        self.reset()


class IoException(Exception):
    pass

class Level(object):
    def __init__(self, level_type=None):
        if level_type is None:
          level_type = Levels.NEW
        self.message = None
        self.type = level_type
        self.precedence = 0

    def attach_and_replace(level, w_message):
        level.attach(w_message)
        level.type = Levels.ATTACH
      	level.message = w_message

    def attach(self, w_message):
        if self.type == Levels.ATTACH:
            # print "Setting next message of %s to %s" % (self.message.name, w_message.name)
            self.message.next = w_message
        elif self.type == Levels.ARG:
            # print "Adding Argument to %s(%s)" % (self.message.name, w_message.name)
            self.message.arguments.append(w_message)
        elif self.type == Levels.NEW:
            # print "Setting message to %s" % (w_message.name,)
            self.message = w_message
        elif self.type == Levels.UNUSED:
            pass

    def finish(self, expressions):
        if self.message is not None:
            self.message.next = None
            # Remove extra () we added in for operators, but do not need any more
            if len(self.message.arguments) == 1:
                arg = self.message.arguments[0]

                # Help annotator
                assert isinstance(arg, io.model.W_Message)

                if (arg.name == '' and len(arg.arguments) == 1
                                                        and arg.next is None):
                    del self.message.arguments[0:]
                    self.message.arguments = arg.arguments
                    arg.arguments = []
            assert isinstance(self.message.arguments, list)
        self.type = Levels.UNUSED

    def __repr__(self):
        return "<Level type=%s precedence=%d message=%s" % (self.name_for_type(), self.precedence, self.message)

    def name_for_type(self):
        if self.type == Levels.ATTACH:
            return 'ATTACH'
        if self.type == Levels.ARG:
            return 'ARG'
        if self.type == Levels.NEW:
            return 'NEW'
        else:
            return 'UNUSED'
    def set_waiting_for_first_arg(self, w_message, precedence):
       self.type = Levels.ARG
       self.message = w_message
       self.precedence = precedence

