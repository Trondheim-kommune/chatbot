import server


class DialogFlowController:
    """
    This class should be between the dialogflow API and the MongoDB (model).
    It should be able to handle: get and create both entities and intents.
    """

    def create_intents(self, intents):
        """
        :param intents: The intents you want to create. Check
        https://github.com/vegarab/agent-25/wiki/Flask-API-formats
        for format.
        :return: A counter of how many intents created.
        """
        return server.batch_create_intents(intents)

    def get_intents(self):
        """
        :return: a PageIterator. Can be used like this:
        for intent in get_all_intents():
            print(intent)
        """
        return server.get_all_intents()

    def create_entities(self, entity_types):
        """
        :param entity_types: A list of entity types. Check
        https://github.com/vegarab/agent-25/wiki/Flask-API-formats
        for format.
        :return: a list of the entity ID's created.
        """
        return server.batch_create_entities(entity_types)

    def get_entities(self):
        """
        :return: This just returns the already cached entities in the server
        module. This might be a bad idea and may change in the future to be
        more like get_intents.
        """
        return server.entities
