from io.register import register_method
from io.model import W_Number, W_Message
@register_method('List', 'append')
def list_append(space, w_target, w_message, w_context):
    assert w_message.arguments,  'requires at least one argument'
    items_w = [x.eval(space, w_target, w_context) for x in w_message.arguments]
    w_target.extend(items_w)
    return w_target

@register_method('List', 'at', unwrap_spec=[object, int])
def list_at(space, target, argument):
    try:
        return target.list_items[argument]
    except IndexError:
        return space.w_nil

@register_method('List', 'foreach')
def list_foreach(space, w_target, w_message, w_context):
    argcount = len(w_message.arguments)
    assert argcount > 0

    # Help annotator
    t = None
    
    body = w_message.arguments[-1]
    if argcount == 3:
        key = w_message.arguments[0].name
        value = w_message.arguments[1].name

        for i in range(len(w_target.list_items)):
            w_context.slots[key] = W_Number(space, i)
            w_context.slots[value] = w_target.list_items[i]
            t = body.eval(space, w_context, w_context)
    elif argcount == 2:
        value = w_message.arguments[0].name

        for i in range(len(w_target.list_items)):
            w_context.slots[value] = w_target.list_items[i]
            t = body.eval(space, w_context, w_context)
    
    elif argcount == 1:
        for i in range(len(w_target.list_items)):
            t = body.eval(space, w_context, w_context)

    return t 
    
@register_method('List', 'with')
def list_with(space, w_target, w_message, w_context):
    new_w_list = w_target.clone()
    items_w = [x.eval(space, w_target, w_context) for x in w_message.arguments]
    new_w_list.extend(items_w)
    return new_w_list
    
# TODO: Not sure if this is rpython
@register_method('List', 'indexOf', unwrap_spec=[object, object])
def list_index_of(space, w_target, item):
    try:
        return W_Number(space, w_target.list_items.index(item))
    except ValueError, e:
        return space.w_nil

# TODO: Not sure if this is rpython
@register_method('List', 'contains', unwrap_spec=[object, object])
def list_contains(space, w_target, item):
    if item in w_target.list_items:
        return space.w_true
    return space.w_false
    
@register_method('List', 'size')
def list_size(space, w_target, w_message, w_context):
    return W_Number(space, len(w_target.list_items))
    
@register_method('List', 'first')
def list_first(space, w_target, w_message, w_context):
    if len(w_message.arguments) != 0:
        t = w_message.arguments[0].eval(space, w_target, w_context)
        assert isinstance(t, W_Number)
        nfirst = int(t.number_value)
    else:
        nfirst = 1
    
    if len(w_target.list_items) == 0 and nfirst == 1:
        return space.w_nil
    
    if nfirst == 1:
        return w_target.list_items[0]
    flist_w = w_target.clone()
    if nfirst < 1:
        flist_w.list_items = []
    else:
        flist_w.list_items = flist_w.list_items[0:nfirst]
    return flist_w
    
@register_method('List', 'last')
def list_last(space, w_target, w_message, w_context):
    if len(w_message.arguments) != 0:
        t = w_message.arguments[0].eval(space, w_target, w_context)
        assert isinstance(t, W_Number)
        nlast = int(t.number_value)
    else:
        nlast = 1
    
    if len(w_target.list_items) == 0 and nlast == 1:
        return space.w_nil
    
    if nlast == 1:
        return w_target.list_items[len(w_target.list_items) - 1]
    flist_w = w_target.clone()
    if nlast < 1:
        flist_w.list_items = []
    else:
        start = len(flist_w.list_items) - nlast
        if start < 0:
            start = 0
        flist_w.list_items = flist_w.list_items[start:]
    return flist_w

@register_method('List', 'reverseInPlace')
def list_reverse_in_place(space, w_target, w_message, w_context):
    w_target.list_items.reverse()
    return w_target
    
@register_method('List', 'removeAll')
def list_remove_all(space, w_target, w_message, w_context):
    try:
        w_target.list_items = []
    except Exception, e:
        raise Exception, 'index out of bounds'

    return w_target

@register_method('List', 'remove')
def list_remove_all(space, w_target, w_message, w_context):
    w_item = w_message.arguments[0].eval(space, w_context, w_context)
    try:
        w_target.list_items.remove(w_item)
    finally:
        return w_target

@register_method('List', 'atPut')
def list_reverse_in_place(space, w_target, w_message, w_context):
    # Help annotator
    assert isinstance(w_message.arguments[0], W_Message)

    w_key = w_message.arguments[0].eval(space, w_target, w_context)
    assert isinstance(w_key, W_Number), "argument 0 to method 'atPut' must be a Number"
    key = int(w_key.number_value)
    if len(w_message.arguments) > 1:
        w_value = w_message.arguments[1].eval(space, w_target, w_context)
    else:
        w_value = space.w_nil
        
    w_target.list_items[key] = w_value
    return w_target
    
