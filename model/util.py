# Create indexing based on three different keyword fields
# Set the default language to norwegian to map similar words


def set_index(collection):
    factory.get_collection(collection).create_index(
        [("keywords", TEXT), ("content.keywords.keyword", TEXT),
         ("header_meta_keywords", TEXT)], default_language="norwegian")
