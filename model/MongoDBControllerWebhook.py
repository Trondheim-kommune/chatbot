from model.ModelFactory import ModelFactory
import random
import model.db_util as util


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
        factory = ModelFactory.get_instance()
        util.set_db(factory, db="dev_db")

        """if intent == "Default Fallback Intent":
            print("we fallin back boys")
            return "fallback"""""

        docs = factory.get_document(raw_query_text, "dev")

        try:
            answers = ' '
            for doc in docs:
                answers += doc['content']['texts'][0] + '-------'

            print(answers)
            return answers
            #return random.choice(texts)
        except KeyError:
            raise Exception("Document doesn't have content and texts. "
                            "Unable to retrieve text from document in dbcontroller webhook")
        #finally:
            #return "Jeg fant ikke informasjonen du spurte etter."
