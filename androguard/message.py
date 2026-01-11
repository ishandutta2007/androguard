class Message:
    pass


class MessageEvent(Message):
    def __init__(
        self, index, function_callee, function_call, params, ret_value
    ):
        self.index = index
        self.from_method = function_call
        self.to_method = function_callee
        self.params = params
        self.ret_value = ret_value


class MessageSystem(Message):
    def __init__(
        self, index, function_callee, function_call, params, information
    ):
        self.index = index
        self.from_method = function_call
        self.to_method = function_callee
        self.params = params
        self.ret_value = information

