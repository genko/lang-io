from io.register import register_method
from io.model import W_ImmutableSequence, W_Number, W_List

@register_method('Map', 'atPut', unwrap_spec=[object, object, object])
def map_at_put(space, w_target, w_key, w_value):
    assert isinstance(w_key, W_ImmutableSequence)
    w_target.at_put(w_key.value, w_value)
    return w_target

@register_method('Map', 'at', unwrap_spec=[object, object])
def map_at(space, w_target, w_key):
    assert isinstance(w_key, W_ImmutableSequence)
    t = w_target.at(w_key.value)
    if t is None:
        return space.w_nil
    return t

@register_method('Map', 'empty')
def map_empty(space, w_target, w_message, w_context):
    w_target.empty()
    return w_target

@register_method('Map', 'atIfAbsentPut', unwrap_spec=[object, object, object])
def map_at_if_absent_put(space, w_target, w_key, w_value):
    assert isinstance(w_key, W_ImmutableSequence)
    key = w_key.value
    if w_target.has_key(key):
        return w_target.at(key)
    w_target.at_put(key, w_value)
    return w_value

@register_method('Map', 'hasKey', unwrap_spec=[object, object])
def map_has_key(space, w_target, w_key):
    assert isinstance(w_key, W_ImmutableSequence)
    if w_target.has_key(w_key.value):
        return space.w_true
    return space.w_false

@register_method('Map', 'size')
def map_size(space, w_target, w_message, w_context):
    return W_Number(space, w_target.size())

@register_method('Map', 'removeAt', unwrap_spec=[object, object])
def map_has_key(space, w_target, w_key):
    assert isinstance(w_key, W_ImmutableSequence)
    w_target.remove_at(w_key.value)
    return w_target

@register_method('Map', 'hasValue', unwrap_spec=[object, object])
def map_has_value(space, w_target, w_value):
    if w_target.has_value(w_value):
        return space.w_true
    return space.w_false

@register_method('Map', 'values')
def map_values(space, w_target, w_message, w_context):
    return space.w_list.clone_and_init(space, w_target.values())

@register_method('Map', 'foreach')
def map_foreach(space, w_target, w_message, w_context):
    argcount = len(w_message.arguments)
    assert argcount == 3
    key = w_message.arguments[0].name
    value = w_message.arguments[1].name

    return w_target.foreach(space, key, value, w_message.arguments[2], w_context)

@register_method('Map', 'keys')
def map_keys(space, w_target, w_message, w_context):
    return space.w_list.clone_and_init(space, w_target.keys())
