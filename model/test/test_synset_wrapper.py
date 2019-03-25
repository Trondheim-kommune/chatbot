from model.SynsetWrapper import SynsetWrapper
import pytest


def test_synset_wrapper_singleton_constructor():
    SynsetWrapper.get_instance()
    with pytest.raises(Exception):
        assert SynsetWrapper()


def test_synset_wrapper_get_instance():
    wrapper = SynsetWrapper.get_instance()
    assert wrapper


def test_get_synset_list():
    # This test is kind of jank.. if you remove the tlf-epost connection it
    # will fail.. Could have a test-synset file, but the wrapper gets kind of
    # messy if we have to add a flag. Should look at this whenever the path to
    # the synset file is added to the global config file
    wrapper = SynsetWrapper.get_instance()
    synset = wrapper.get_synset('tlf')
    assert 'epost' in synset
