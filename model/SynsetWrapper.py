from util.config_util import Config
import copy


SYNSET_FILE = Config.get_value(['query_system', 'custom_synset_file'])


class SynsetWrapper():
    ''' Wrapper for a custom synset list. Interfaces with a text file where
    each line consists of synonyms split by comma '''
    __instance = None

    @staticmethod
    def get_instance():
        ''' Static access method '''
        if SynsetWrapper.__instance is None:
            SynsetWrapper()
        return SynsetWrapper.__instance

    def __init__(self):
        ''' Virtually private constrcutor '''
        if SynsetWrapper.__instance is not None:
            raise Exception('This class is a singleton!')
        else:
            self.__read_synset_file()
            SynsetWrapper.__instance = self

    def get_synset(self, token):
        ''' Return a synset for a given token '''
        return next((copy.deepcopy(synset) for synset in self.synset_list
                    if token in synset), None)

    @staticmethod
    def synset_file_updated():
        ''' Updates the cached synset list whenever the textfile is updated '''
        SynsetWrapper.get_instance().__read_synset_file()

    def __read_synset_file(self):
        ''' Read the contents of the synset file and add them to the
        synset_list '''
        with open(SYNSET_FILE) as synset_file:
            self.synset_list = [
                [word.strip() for word in line.split(',')]
                for line in synset_file
            ]
