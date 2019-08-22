from chatbot.nlp.query import QueryHandler


handler = QueryHandler()


class DirectResponse(object):
    def __init__(self, user_input=''):
        self.user_input = user_input
        self.response = handler.get_response(self.user_input)


class Response(object):
    def __init__(self, user_input='', response_format='plain'):
        self.user_input = user_input
        self.response_format = response_format
        self.response = handler.get_response(self.user_input,
                                             self.response_format)


class Conflict(object):
    def __init__(self, conflict_id, title):
        self.conflict_id = conflict_id
        self.title = title


class Document(object):
    def __init__(self, id, title):
        self.id = id
        self.title = title
