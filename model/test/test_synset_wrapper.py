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
    # Beware that this might fail if the tlf - epost connection is removed from
    # the synset file
    wrapper = SynsetWrapper.get_instance()
    synset = wrapper.get_synset('tlf')
    assert 'epost' in synset
