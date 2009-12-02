from pypy.lang.io.register import register_method
from pypy.lang.io.model import W_ImmutableSequence, W_Block, W_Number

@register_method('Object', 'setSlot', unwrap_spec=[object, str, object])
def w_object_set_slot(space, w_target, name, w_value):
    w_target.slots[name] = w_value
    return w_value
    
@register_method('Object', 'setSlotWithType', unwrap_spec=[object, str, object])
def w_object_set_slot_with_type(space, w_target, name, w_value):
    w_object_set_slot(space, w_target, name, w_value)
    w_object_set_slot(space, w_value, "type", space.w_immutable_sequence.clone_and_init(name))
    return w_value

@register_method('Object', 'getSlot', unwrap_spec=[object, str])
def w_object_get_slot(space, w_target, name):
    try:
        return w_target.slots[name]
    except KeyError:
        return space.w_nil

@register_method('Object', 'hasSlot', unwrap_spec=[object, str])
def w_object_has_slot(space, w_target, name):
    if w_target.lookup(name) is None:
        return space.w_false
    return space.w_true

@register_method('Object', '?')
def w_object_question_mark(space, w_target, w_message, w_context):
    name = w_message.arguments[0].name
    if w_object_has_slot(space, w_target, name) is space.w_false:
        return space.w_nil
    return w_message.arguments[0].eval(space, w_target, w_context)
    
@register_method('Object', 'method')
def w_object_method(space, w_target, w_message, w_context):
    w_body = w_message.arguments[-1]
    w_arguments = w_message.arguments[:-1]
    names = [x.name for x in w_arguments]
    return space.w_block.clone_and_init(space, names, w_body, True)

@register_method('Object', 'block')
def w_object_block(space, w_target, w_message, w_context):
    w_body = w_message.arguments[-1]
    w_arguments = w_message.arguments[:-1]
    names = [x.name for x in w_arguments]
    return space.w_block.clone_and_init(space, names, w_body, False)
    
@register_method('Object', 'clone', unwrap_spec=[object])
def w_object_clone(space, w_target):
    return w_target.clone()

@register_method('Object', 'list')
def w_object_list(space, w_target, w_message, w_context):
    w_items = [x.eval(space, w_target, w_context) for x in w_message.arguments]
    return space.w_list.clone_and_init(space, w_items)
    
@register_method('Object', 'do')
def w_object_do(space, w_target, w_message, w_context):
    w_message.arguments[0].eval(space, w_target, w_target)
    return w_target
    
@register_method('Object', '', unwrap_spec=[object, object])
def w_object_(space, w_target, w_arg):
    return w_arg


@register_method('Object', 'message')
def object_message(space, w_target, w_message, w_context):
    return w_message.arguments[0]
    
@register_method('Object', '-', unwrap_spec=[object, float])
def object_minus(space, w_target, argument):
    return W_Number(space, -argument)
    
@register_method('Object', 'debugger')
def object_message(space, w_target, w_message, w_context):
    import pdb
    pdb.set_trace()
    return w_target

@register_method('Object', 'for')
def object_for(space, w_target, w_message, w_context):
   argcount = len(w_message.arguments)
   assert argcount >= 4 and argcount <=5

   body = w_message.arguments[-1]
   start = w_message.arguments[1].eval(space, w_target, w_context).value
   stop = 1 + w_message.arguments[2].eval(space, w_target, w_context).value
   if argcount == 4:
      step = 1
   else:
      step = w_message.arguments[3].eval(space, w_message, w_context).value
   
      
   key = w_message.arguments[0].name
   
   space.normal_status()
   for i in range(start, stop, step):
      w_context.slots[key] = W_Number(space, i)
      t = body.eval(space, w_context, w_context)
      
      if not space.is_normal_status():
          if space.is_continue_status():
              space.normal_status()
          else:
            space.normal_status()
            break
            
   return t
   
@register_method('Object', 'appendProto', unwrap_spec=[object, object])
def object_append_proto(space, w_target, w_proto):
    w_target.protos.append(w_proto)
    return w_target
    
@register_method('Object', 'doMessage',)
def object_do_message(space, w_target, w_message, w_context):
    w_msg = w_message.arguments[0].eval(space, w_context, w_context)
    w_receiver = w_target
    if len(w_message.arguments) == 2:
        w_receiver = w_message.arguments[1].eval(space, w_context, w_context)
        
    return w_msg.eval(space, w_receiver, w_receiver)
    
    
@register_method('Object', 'break')
def object_break(space, w_target, w_message, w_context):
    w_result = space.w_nil
    if len(w_message.arguments) > 0:
        w_result = w_message.arguments[0].eval(space, w_context, w_context)
    space.break_status(w_result)
    return w_target
    
    
@register_method('Object', 'continue')
def object_continue(space, w_target, w_message, w_context):
    space.continue_status()
    return w_target
    
@register_method('Object', 'return')
def object_return(space, w_target, w_message, w_context):
    w_value = space.w_nil
    if len(w_message.arguments) > 0:
        w_value = w_message.arguments[0].eval(space, w_context, w_context)
    
    space.return_status(w_value)
    return w_target
    
@register_method('Object', 'if')
def object_if(space, w_target, w_message, w_context):
    w_condition = w_message.arguments[0].eval(space, w_context, w_context)

    if w_condition is space.w_true:
        index = 1 
    else:
        index = 2
        
    if index < len(w_message.arguments):
        return w_message.arguments[index].eval(space, w_context, w_context)
    return w_condition
    
@register_method('Object', 'stopStatus')
def object_stopstatus(space, w_target, w_message, w_context):
    if len(w_message.arguments) > 0:
        w_message.arguments[0].eval(space, w_context, w_context)
    w = space.stop_status
    space.normal_status()
    return w
    
@register_method('Object', 'doString', unwrap_spec=[object, str])
def object_do_string(space, w_target, code):
    # XXX Replace this when the actual parser is done
    from parserhack import parse
    ast = parse(code, space)
    return ast.eval(space, w_target, w_target)
    
    
# XXX replace with the original one in A2_Object.io when it works
@register_method('Object', 'newSlot', unwrap_spec=[object, str, object])
def object_new_slot(space, w_target, name, w_value):
    from pypy.lang.io.model import W_CFunction
    w_target.slots[name] = w_value

    def setSlot(my_space, w_w_target, w_w_message, w_w_context):
        w_w_target.slots[name] = w_w_message.arguments[0].eval(my_space, 
                                                                w_w_context,
                                                                w_w_target)
        return w_w_target

    w_target.slots['set%s' % (name[0].capitalize() + name[1:])] = W_CFunction(space, setSlot)
    
@register_method('Object', 'updateSlot', unwrap_spec=[object, str, object])
def object_update_slot(space, w_target, slotname, w_value):
    assert w_target.lookup(slotname) is not None

    w_target.slots[slotname] = w_value
    return w_value
    
@register_method('Object', 'write')
def object_write(space, w_target, w_message, w_context):
    for x in w_message.arguments:
        e = x.eval(space, w_context, w_context)
        space.w_print_message.eval(space, e, w_context)
    return space.w_nil