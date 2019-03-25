class SynsetWrapper():
    ''' Wrapper for a custom synset list. Interfaces with a text file where
    each line consists of synonyms split by comma '''

    def __init__(self):
        self.__read_synset_file()
    
    def get_synset(self, token):
        ''' Return a synset for a given token '''
        for synset in self.synset_list:
            if token in synset: return synset

    def __read_synset_file(self):
        ''' Read the contents of the synset file and add them to the
        synset_list'''
        # Put this in the global config
        path = 'model/synset'

        with open(path) as synset_file:
            self.synset_list = [line.replace(' ','').strip().split(',') for line in synset_file]

