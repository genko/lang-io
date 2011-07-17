from io.register import register_method
from io.model import W_Message, W_ImmutableSequence

@register_method('Sequence', '..', unwrap_spec=[object, str])
def sequence_append(space, w_sequence, w_append_seq):
    s = space.w_sequence.clone()
    s.value = w_sequence.value + w_append_seq
    return s
    
@register_method('Sequence', 'asCapitalized')
def sequence_as_capitalized(space, w_target, w_message, w_context):
    # c/p from pypy/objspace/std/stringobject.py
    input = w_target.value
    buffer = [' '] * len(input)
    if len(input) > 0:
        ch = input[0]
        if ch.islower():
            o = ord(ch) - 32
            buffer[0] = chr(o)
        else:
            buffer[0] = ch

        for i in range(1, len(input)):
            ch = input[i]
            if ch.isupper():
                o = ord(ch) + 32
                buffer[i] = chr(o)
            else:
                buffer[i] = ch

    s = space.w_sequence.clone()
    s.value = "".join(buffer)
    return s
