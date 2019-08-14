from model.QuerySystem import QuerySystem

handler = QuerySystem()

while True:
    text = input('> ')
    print()
    print(handler.get_response(text))
    print()
