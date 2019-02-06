class InvalidDialogFlowID(Exception):
    """
    This exception is thrown when you try to create entities/ intents that already exists, or when
    you try to delete something that does not exist.
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        """
        :param message: The exception message to be printed out.
        :param status_code: Which status_code should be used, default 400.
        :param payload: Extra information you want to return.
        """
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["status"] = "ERROR"
        rv["message"] = self.message
        return rv
