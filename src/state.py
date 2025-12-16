import logging

from src.constants import MODEL_MAX_TOKENS

logger = logging.getLogger(__name__)


class MessagesState(object):
    """
    Simple class to store current agent state as series of
    messages
    """

    def __init__(self):
        self.messages = []

    def update(self, message: dict):
        self.messages.append(message)
        # roughly estimate token usage as word_count * 2
        if 2 * len(str(self.messages).split(" ")) >= MODEL_MAX_TOKENS:
            err_msg = "Token limit achieved during execution"
            logger.error(err_msg)
            raise Exception(err_msg)

    def batch_update(self, messages: list[dict]):
        self.messages += messages
        # roughly estimate token usage as word_count * 2
        if 2 * len(str(self.messages).split(" ")) >= MODEL_MAX_TOKENS:
            err_msg = "Token limit achieved during execution"
            logger.error(err_msg)
            raise Exception(err_msg)

    def construct_prompt(self):
        return self.messages
