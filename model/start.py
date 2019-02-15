import sys
import os
import util
from progressbar import ProgressBar

from model.Serializer import Serializer
from model.ModelFactory import ModelFactory


def main():
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        raise ValueError('No data-file path provided')

    ser = Serializer(filepath)
    ser.serialize_data()
    data = ser.get_models()

    factory = ModelFactory.get_instance()

    factory.set_database("agent25.tinusf.com", "dev_db",
                         str(os.getenv('DB_USER')), str(os.getenv("DB_PWD")))

    # Drop database due to duplicate data when running this
    factory.get_database().drop_collection("dev")

    print('Starting insertion of {} documents'.format(len(data)))
    pbar = ProgressBar()
    for i, doc in enumerate(pbar(data)):
        factory.post_document(doc, "dev")
    print('Successfully inserted {} documents'.format(i + 1))

    util.set_index("dev", factory)


if __name__ == '__main__':
    main()
