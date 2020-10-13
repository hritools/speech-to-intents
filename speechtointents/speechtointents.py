from speechtointents.solutions.sti.sti import SpeechToTextToIntentSimple, SpeechToTextToIntentSimpleTrainer

class SpeechToIntents:
    def __init__(self, intents, solution=SpeechToTextToIntentSimple):
        self.intents  = intents
        self.solution = solution(intents)

        # TODO: Scan all the solutions and find one suitable for all of the provided intents.
        # TODO: Define an ordering between the solutions.

    def parse(self, speech):
        """
        Returns a sequence of intents.
        The format of speech is undefined yet.
        """
        return self.solution.parse(speech)

    def validate(self, dataset):
        """
        It is recommended to validate the semantic parser on your particular dataset.
        (speech, intent_keyword, slot_value)
        Supports only one intent with one slot.

        Returns:
            sklearn classification report
        """
        return self.solution.validate(dataset)

    def fit(self, dataset):
        """
        Finds the optimal parametrization of the current solution for the provided dataset (inplace).

        Returns:
            best metric (float), best sklearn classification report (dict)
        """
        return self.solution.fit(dataset)