import ModelFactory as mf
import os
from Random import random


class MongoDBControllerWebhook:
    """
    This class should be between the dialogflow API and the MongoDB (model).
    It should handle when a user asks a question.
    """

    def webhook_query(self, raw_query_text, intent, entities, default_text):
        """
        Called when a user asks a question.
        dialogflow --> Flask --> Controller --> model --> controller -->
        flask --> dialogflow

        :param raw_query_text: This is the full query text from the user.
        :param intent: The intent that got automatically matched.
        :param entities: The entities that got matched.
        :param default_text: The randomly chosen static reply if the intent
        has any.

        :return: This should just return a simple string.
        """
        print("raw_query_text", raw_query_text)
        print("intent:", intent)
        print("entities:", entities)
        print("default_text:", default_text)

        # Connect to database to retrieve documents
        model_factory = mf.ModelFactory()
        model_factory.set_database("agent25.tinusf.com", "test_db",
                                   str(os.getenv('DB_USER')), str(os.getenv('DB_PWD')))

        if intent == "Default Fallback Intent":
            print("we fallin back boys")
            return "fallback"

        doc = model_factory.get_document(" ".join(entities), "test2")

        try:
            texts = doc['content']['texts']
            return texts[random.randint(0, len(texts)-1)]
        except KeyError:
            raise Exception("Document doesn't have content and texts. "
                  "Unable to retrieve text from document in dbcontroller webhook")
        finally:
            return "Jeg fant ikke informasjonen du spurte etter."


