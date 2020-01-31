from chatbot.nlp.query import QueryHandler


handler = QueryHandler()


class Response(object):
    def __init__(self, user_input, style, source, session=None):
        self.user_input = user_input
        self.response = handler.get_response(self.user_input, style, source)
        self.style = style
        self.source = source
        self.session = session

class Conflict(object):
    def __init__(self, conflict_id, title):
        self.id = conflict_id
        self.title = title


class Document(object):
    def __init__(self, id, title):
        self.id = id
        self.title = title
