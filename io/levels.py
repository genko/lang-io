import io
class Levels(object):
    NEW = 0
    ATTACH = 1
    ARG = 2
    UNUSED = 3
    IO_OP_MAX_LEVEL = 32
    
    def __init__(self, space, w_message):
        super(Levels, self).__init__()
        self.space = space
        if 'OperatorTable' not in w_message.slots:
            print "OperatorTable not in message slots"
            if 'OperatorTable' not in space.w_core.slots:
                print "OperatorTable not in Core slots"
                # create a new one in state.w_core
                operator_table = space.w_object.clone()
                space.w_core.slots['OperatorTable'] = operator_table
                operator_table.slots['precedenceLevelCount'] = Levels.IO_OP_MAX_LEVEL
            else:
                operator_table = space.w_core.slots['OperatorTable']
        else:
            operator_table = w_message.slots['OperatorTable']
        self.operator_table = self._get_op_table(operator_table, 'operators', self._create_operator_table)
        self.assign_operator_table = self._get_op_table(operator_table, 'assignOperators', self._create_assign_operator_table)
        self.current_level_precedence = 1
        self.stack = [Level(None, Levels.NEW, Levels.IO_OP_MAX_LEVEL)]
    
    def _create_assign_operator_table(self):
        ass_op_table = self.space.w_map.clone()
        ass_op_table.at_put(self.space.newsequence(':='), self.space.newsequence('setSlot'))
        ass_op_table.at_put(self.space.newsequence('='), self.space.newsequence('updateSlot'))
        ass_op_table.at_put(self.space.newsequence('::='), self.space.newsequence('newSlot'))
        return ass_op_table
   
    def _create_operator_table(self):
        print "_create_operator_table called"
        table = {"@": 0, "@@": 0, "?": 0, "**": 1, "*": 2, "/": 2, "%": 2, 
        "+": 3, "-": 3, "<<": 4, ">>": 4, ">": 5, "<": 5, "<=": 5, ">=": 5, 
        "==": 6, "!=": 6, "&": 7, "^": 8, "|": 9, "and": 10, "&&": 10, 
        "or": 11, "||": 11, "..": 12, "+=": 13, "-=": 13, "*=": 13, "/=": 13,
        "%=": 13, "&=": 13, "^=": 13, "|=": 13, "<<=": 13, ">>=": 13, 
        "return": 14}
        op_table = self.space.w_map.clone()
        for key in table:
            op_table.at_put(self.space.newsequence(key),
                            io.model.W_Number(self.space, table[key]))
        return op_table
   
    def _get_op_table(self, operator_table, slot_name, callback):
        if slot_name in operator_table.slots and isinstance(operator_table.slots[slot_name], io.model.W_Map):
            return operator_table.slots[slot_name]
            
        else:
            # Ref: IoMessage_opShuffle.c line 155
            # Not strictly correct as if the message has its own empty
            # OperatorTable slot, we'll create one for it instead of using
            # Core Message OperatorTable operators. Oh well.
            result = callback()
            operator_table.slots[slot_name] = result
            return result
            
    def current_level(self):
        if len(self.stack) == 0:
            return None
        return self.stack[-1]
    
    def attach(self, w_message, expressions):
        print "attach(%r, %r)" % (w_message, expressions)
        # XXX clean up this method.
        precedence = self._level_for_op(w_message)
        print "precedence of %s is %d" % (w_message.name, precedence)
        if self._is_assign_operator(w_message):
            current_level = self.current_level()
            attaching = current_level.message
            if attaching is None:
                # XXX raise an error
                print "compile error: %s requires a symbol to its left." % w_message.name
                return
            if len(attaching.arguments) > 0:
                # XXX raise an error
                print "compile error: The symbol to the left of %s cannot have arguments." % w_message.name
                return
            if len(w_message.arguments) > 1:
                # XXX raise an error
                print "compile error: Assign operator passed multiple arguments, e.g., a := (b, c)." % w_message.name
                return
            # a := b ;
            slot_name_message = W_Message(self.space, "%s" % attaching.name, [])
            # slot_name_message.update_source_location(attaching)            
            # a := b ;  ->  a("a") := b ;
            attaching.arguments.append(slot_name_message)         
            
            set_slot_name = self._name_for_assign_operator(w_message, slot_name_message)
            attaching.name =  set_slot_name
            self.current_level().type = Levels.ATTACH
            if len(w_message.arguments) > 0: #setSlot("a") :=(b c) d e ;
                # b c
                arg = w_message.arguments[0]
                if w_message.next is None or w_message.next.name == ';':
                    attaching.arguments.append(arg)
                else:
                    # ()
                    foo = W_Message(self.space, '', [])
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
                    print "compile error: %s must be followed by a value." % w_message.name
                    return
                # setSlot("a") := b c ;  ->  setSlot("a", b c ;) := b c ;
                attaching.arguments.append(w_message.next)
            
            # process the value (b c d) later  (setSlot("a", b c d) := b c d ;)
            if w_message.next is not None and not w_message.next.name == ';':
                expressions.append(w_message.next)
            last = w_message
            while last.next is not None and not w_message.next.name == ';':
                last = last.next
            
            attaching.next = last.next

            # Continue processing in IoMessage_opShuffle loop
            w_message.next = last.next
            
            if last is not w_message:
                last.next = None

            # make sure b in 1 := b gets executed
            attaching.literal_value = None
        elif w_message.name == ';':
            print "message name is ;"
            self._pop_down_to(Levels.IO_OP_MAX_LEVEL-1)
            self.current_level().attach_and_replace(w_message)
        elif precedence != -1:
            if len(w_message.arguments) > 0:
                # move arguments off to their own message to make () after operators behave like Cs grouping ()
                brackets = io.model.W_Message(self.space, "", [])
                # XXX IoMessage_rawCopySourceLocation(brackets, msg);
                brackets.arguments = w_message.arguments
                w_message.arguments = []
                # Insert the brackets message between msg and its next message
                brackets.next = w_message.next
                w_message.next = brackets
            self._pop_down_to(precedence)
            self._attach_to_top_and_push(w_message, precedence)
        else:
            self.current_level().attach_and_replace(w_message)

    def _attach_to_top_and_push(self, w_message, precedence):
        top = self.stack[-1]
        top.attach_and_replace(w_message)
        # XXX Check for overflow of the pool.
        print 'current_level_precedence is %d' % self.current_level_precedence
        if self.current_level_precedence >= Levels.IO_OP_MAX_LEVEL:
            # XXX raise an error
            print "compile error: Overflowed operator stack. Only %d levels \
                    of operators currently supported." % (Levels.IO_OP_MAX_LEVEL-1)
            return
        self.current_level_precedence +=1
        level = Level(w_message, Levels.ARG, self.current_level_precedence)
        self.stack.append(level)
        print self.stack

    def _name_for_assign_operator(self, operator, slot):
        operator_name = operator.name
        value = self.assign_operator_table.at(
                                        self.space.newsequence(operator_name))
        if value is not self.space.w_nil and isinstance(value, 
                                                io.model.W_ImmutableSequence):
            if operator_name == ":=" and slot.name[0].isupper():
                return self.space.newsequence("setSlotWithType")
            else:
                return value
        else:
            raise IoException("compile error: Value for '%s' in Message \
                    OperatorTable assignOperators is not a symbol. Values in \
                    the OperatorTable assignOperators are symbols which are \
                    the name of the operator." % operator_name)

    def _pop_down_to(self, target_level):
        level = self.current_level() 
        while (level.precedence <= target_level
                    and level.type != Levels.ARG):
    		self.stack.pop().finish()
    		self.current_level_precedence -= 1
    		level = self.current_level() 
    
    def _is_assign_operator(self, w_message):
        message_name = self.space.newsequence(w_message.name)
        return self.assign_operator_table.has_key(message_name)
        
    def _level_for_op(self, w_message):
        message_name = self.space.newsequence(w_message.name)
        if not self.operator_table.has_key(message_name):
            print "%s not found in the operator_table slots" % w_message.name
            return -1
        operator = self.operator_table.at(message_name)
        if type(operator) == io.model.W_Number:
            value = operator.value
            if value < 0 or value >= Levels.IO_OP_MAX_LEVEL:
                #'XXX Some corresponding exception'#error
                raise IoException("compile error: Precedence for operators \
                    must be between 0 and %d. Precedence was %d." 
                    % (Levels.IO_OP_MAX_LEVEL - 1, value))
            return value
        else:
            raise IoException("compile error: Value for '%s' in Message \
                OperatorTable operators is not a number. Values in the \
                OperatorTable operators are numbers which indicate the \
                precedence of the operator." % w_message.name)
            
    def next_message(self):
        while len(self.stack) > 0:
            level = self.stack.pop()
            level.finish()

class IoException(Exception):
    pass
class Level(object):
    def __init__(self, w_message, level_type, precedence):
        super(Level, self).__init__()
        self.message = w_message
        self.type = level_type
        self.precedence = precedence
        
    def attach_and_replace(self, w_message):
        print "attach and replace %r" % self
        self.attach(w_message)
        self.type = Levels.ATTACH
    	self.message = w_message
    	
    def attach(self, w_message):
        if self.type == Levels.ATTACH:
            print "Setting next message of %s to %s" % (self.message.name, w_message.name)
            self.message.next = w_message
    	elif self.type == Levels.ARG:
    	    print "Adding Argument to %s(%s)" % (self.message.name, w_message.name) 
    	    self.message.arguments.append(w_message)
        elif self.type == Levels.NEW:
            print "Setting message to %s" % (w_message.name,)
            self.message = w_message
        elif self.type == Levels.UNUSED:
            pass
 
    def finish(self):
        if self.message:
            self.message.next = None
            # Remove extra () we added in for operators, but do not need any more
            if len(self.message.arguments) == 1:
                arg = self.message.arguments[0]
                if (arg.name == '' and len(arg.arguments) == 1 
                                                        and arg.next == None):
                    self.message.arguments = arg.arguments
                    arg.arguments = []
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