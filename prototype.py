from chatbot.nlp.query import QueryHandler

handler = QueryHandler()

while True:
    text = input('> ')
    print()
    print(handler.get_response(text))
    print()
