from chatbot.nlp.query import QueryHandler


handler = QueryHandler()


class Response(object):
    def __init__(self, user_input, style):
        self.user_input = user_input
        if style: 
            self.response = handler.get_response(self.user_input, style)
        else: 
            self.response = handler.get_response(self.user_input)
        self.style = style


class Conflict(object):
    def __init__(self, conflict_id, title):
        self.id = conflict_id
        self.title = title


class Document(object):
    def __init__(self, id, title):
        self.id = id
        self.title = title
