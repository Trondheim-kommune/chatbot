import logging


def set_logger():
    log_format = "%(asctime)s::%(levelname)s::%(name)s::"\
                 "%(filename)s::%(lineno)d::%(message)s"
    logging.basicConfig(filename='logs/chatbot.log', level='DEBUG',
                        format=log_format)
