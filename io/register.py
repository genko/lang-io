from io import model
cfunction_definitions = {}

def _create_wrapper(function, unwrap_spec):
    import ast, copy
    tree = ast.parse("def wrapper(space, w_target, w_message, w_context):\n"
                     "    evaled_w = [w_target]\n"
                     "    for arg in w_message.arguments:\n"
                     "        evaled_w.append(arg.eval(space, w_context, w_context))\n"
                     "    return func(space, evaled_w[0])")
    # Now modify the call arguments
    call = tree.body[0].body[-1].value
    subscript = call.args[-1]
    call.args.pop()

    def create_convert_call(name, node):
        call_node = copy.deepcopy(call)
        call_node.func.id = name
        call_node.args = [call.args[0], node]
        return call_node

    def _convert_float(space, value):
        assert isinstance(value, model.W_Number)
        return value.number_value

    def _convert_int(space, value):
        assert isinstance(value, model.W_Number)
        return int(value.number_value)

    def _convert_str(space, value):
        if isinstance(value, model.W_Number):
            return str(value.number_value)
        else:
            return value.value

    def _convert_bool(space, value):
        return x is space.w_true

    for (i, type_) in enumerate(unwrap_spec):
        node = copy.deepcopy(subscript)
        node.slice.value.n = i
        if type_ is object:
            call.args.append(node)
        elif type_ is float:
            call.args.append(create_convert_call("_convert_float", node))
        elif type_ is int:
            call.args.append(create_convert_call("_convert_int", node))
        elif type_ is str:
            call.args.append(create_convert_call("_convert_str", node))
        elif type_ is bool:
            call_args.append(create_convert_call("_convert_bool", node))
        else:
            raise ValueError('Unknown unwrap spec')
    # Compile the new AST
    code = compile(tree, "<string>", "exec")
    locals_ = dict()
    names = dict(
        func=function, _convert_float=_convert_float,
        _convert_str=_convert_str, _convert_int=_convert_int,
        _convert_bool=_convert_bool
    )
    exec code in names, locals_
    return locals_["wrapper"]

def register_method(type_name, slot_name, unwrap_spec=None, alias=None):
    if alias is None:
        alias = [slot_name]
    else:
        alias.append(slot_name)

    def register(function):
        if unwrap_spec is None:
            wrapper = function
        else:
            wrapper = _create_wrapper(function, unwrap_spec)
        subdict = cfunction_definitions.setdefault(type_name, {})

        for slotn in alias:
            subdict[slotn] = wrapper

        return function

    return register
