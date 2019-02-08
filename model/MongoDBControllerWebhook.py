# import mongoDB's query function


class MongoDBControllerWebhook:
    """
    This class should be between the dialogflow API and the MongoDB (model).
    It should handle when a user asks a question.
    """

    def webhook_query(self, raw_query_text, intent, entities, default_text):
        """
        Called when a user asks a question.
        dialogflow --> Flask --> Controller --> model --> controller --> flask --> dialogflow
        :param raw_query_text: This is the full query text from the user.
        :param intent: The intent that got automatically matched.
        :param entities: The entities that got matched.
        :param default_text: The randomly chosen static reply if the intent has any.

        :return: This should just return a simple string.
        """
        print("raw_query_text", raw_query_text)
        print("intent:", intent)
        print("entities:", entities)
        print("default_text:", default_text)

        if intent == "Default Fallback Intent":
            print("we fallin back boys")
            return "fallback"

        return "Normal"
