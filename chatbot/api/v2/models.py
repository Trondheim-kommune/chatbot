import random

from chatbot.nlp.query import QueryHandler
from chatbot.util.config_util import Config

NOT_FOUND = Config.get_value(['query_system', 'not_found'])
MULTIPLE_ANSWERS = Config.get_value(['query_system', 'multiple_answers'])


handler = QueryHandler()


class Response(object):
    def __init__(self, user_input, style, source, session=None):
        self.user_input = user_input
        if style is None:
            self.response = handler.get_response(self.user_input,
                                                 source=source)
        else:
            self.response = handler.get_response(self.user_input,
                                                 style,
                                                 source)
        self.style = style
        self.source = source
        self.session = session


class ResponseRaw(object):
    def __init__(self, user_input, source, session, style):
        self.user_input = user_input
        responses = handler.get_response(self.user_input,
                                         source=source,
                                         url_style=style,
                                         raw=True)
        self.response = []
        for r in responses:
            answer = {}
            answer['answer'] = r[0]
            answer['links'] = []

            if len(r) > 1:
                # Remove last element (source link)
                answer_source = r[1].pop(-1)
                answer['answer_source'] = {}
                answer['answer_source']['title'] = answer_source[0]
                answer['answer_source']['link'] = answer_source[1]
                for link in r[1]:
                    answer['links'].append({'title': link[0], 'link': link[1]})

            answer['answer_id'] = random.randint(1000, 9999)
            self.response.append(answer)

        # Static ID for default answers
        if (self.response[0]['answer'] == MULTIPLE_ANSWERS or
            self.response[0]['answer'] == NOT_FOUND):
            self.response[0]['answer_id'] = -1


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


class Feedback(object):
    def __init__(self, feedback, session, user_input, answer, answer_id):
        self.feedback = feedback
        self.session = session
        self.user_input = user_input
        self.answer = answer
        self.answer_id = answer_id
