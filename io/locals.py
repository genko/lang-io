from io.register import register_method

@register_method('Locals', 'updateSlot')
def locals_update_slot(space, w_target, w_message, w_context):
    slotname = w_message.arguments[0].eval(space, w_target, w_context).value
    assert w_target.lookup(slotname) is not None

    if slotname in w_target.slots:
        w_value = w_message.arguments[1].eval(space, w_target, w_context)
        w_target.slots[slotname] = w_value
        return w_value
    else:
        w_self = w_target.lookup('self')
        return w_message.eval(space, w_self, w_context)
