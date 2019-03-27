import json
from model.QuerySystem import perform_search


def evaluate_test(test):
    """
    :param test: a dictionary containing a question key and answers key.
    :return: A score between 0 and 1.
    """
    question = test["question"]
    our_answer = perform_search(question)
    correct_answers = test["answers"]
    for correct_answer in correct_answers:
        if correct_answer["text"] in our_answer:
            return correct_answer["point"]

    return 0


def main():
    f = open("model/test/test_data/test_data_evaluation.json")
    raw_file = f.read()
    f.close()
    tests = json.loads(raw_file)

    n_questions = len(tests)
    score = 0

    for test in tests:
        score += evaluate_test(test)
    print("Number of questions: ", n_questions, "score:", score)

    if score == 0:
        print("Average scores: 0")
    else:
        print("Average scores:", n_questions / score)


if __name__ == '__main__':
    main()
