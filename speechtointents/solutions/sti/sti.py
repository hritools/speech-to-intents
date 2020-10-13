import speech_recognition as sr
import pymorphy2
import editdistance
import numpy as np
import string

from sklearn.metrics import classification_report
from collections     import OrderedDict
from tqdm            import tqdm
from itertools       import product


class SpeechToTextToIntentSimpleTrainer:
    def __init__(self, intents):
        pass


class SpeechToTextToIntentSimple:
    def __init__(self, intents, cache_speech_to_text=True):
        for intent in intents:
            if len(intent.get_keywords()) == 0:
                raise Exception("This solution only supports intents with keywords.")

        # Verify that we can work with the provided intents
        if not self.verify_intents(intents):
            raise Exception("This solution does not support some of the provided intents (maybe all, maybe one).")

        self.intents               = intents
        self.text_to_intent        = TextToIntentSimple()
        self.speech_rec            = sr.Recognizer()
        self._cached_speech_text   = {}
        self._cache_speech_to_text = cache_speech_to_text

    def help_text(self):
        return '.\n'.join([intent.help_text() for intent in self.intents])

    def parse(self, speech):
        text   = self._speech_to_text(speech)
        intent = self.text_to_intent.parse(text, self.intents)
        return intent 

    def validate(self, dataset, output_dict=False):
        """
        It is recommended to validate the semantic parser on your particular dataset.
        (speech, intent_keyword, slot_value)
        Supports only one intent with one slot.

        Returns:
            sklearn classification report (either a dictionary or a string, defaults to string)
        """
        # TODO: Make it more explicit (this behaviour is not clear without looking here)
        # TODO: Merge intents found in dataset and the passed intents
        def get_label(intent_keyword, slot_value):
            if slot_value is None:
                slot_value = ""
            return "{}_{}".format(intent_keyword, slot_value)
        def get_label_object(intent):
            # If there was no intent, default to this
            if intent is None:
                return get_label("unknown", "empty")

            if len(intent.concrete_slots) == 0:
                slot_value = "empty"
            else:
                slot_value = intent.concrete_slots[0].value

                # If could not determine the slot, it's unknown
                if slot_value == None:
                    slot_value = "unknown"

            return get_label(intent.KEYWORD, slot_value)

        ### Parse all presented intents and keywords
        found_intents = OrderedDict()
        for record in dataset:
            target_speech         = record[0]
            target_intent_keyword = record[1]
            target_slot_value     = record[2]
            target_name           = get_label(target_intent_keyword, target_slot_value)
            if target_name not in found_intents:
                found_intents[target_name] = len(found_intents)

        ### Make predictions
        y_true, y_pred = [], []
        for record in dataset:
            target_speech         = record[0]
            target_intent_keyword = record[1]
            target_slot_value     = record[2]
            target_name           = get_label(target_intent_keyword, target_slot_value)

            # Predict an intent
            pred_intent = self.parse(target_speech)
            pred_name   = get_label_object(pred_intent)

            if pred_name not in found_intents:
                found_intents[pred_name] = len(found_intents)

            y_true.append(found_intents[target_name])
            y_pred.append(found_intents[pred_name])

        return classification_report(y_true, y_pred, target_names=list(found_intents.keys()), output_dict=output_dict)

    def fit(self, dataset):
        """
        Returns:
            best metric (float), best sklearn classification report (dict)
        """
        def target_metric(report):
            return report["weighted avg"]["f1-score"]

        # Find best distance for unknown intent
        best_metric         = 0.0
        best_report         = None
        best_text_to_intent = None

        start               = 3
        num_steps           = 17
        parameters          = product(range(start, start + num_steps), range(start, start + num_steps))
        for intent_max_dist, slot_max_dist in tqdm(parameters, total=num_steps**2):
            self.text_to_intent = TextToIntentSimple(intent_max_distance=intent_max_dist, slot_max_distance=slot_max_dist)
            cur_report          = self.validate(dataset, output_dict=True)
            cur_metric          = target_metric(cur_report)
            if cur_metric >= best_metric:
                best_report = cur_report
                best_metric = cur_metric
                best_text_to_intent = TextToIntentSimple(intent_max_distance=intent_max_dist, slot_max_distance=slot_max_dist)

        # Set the best found model
        self.text_to_intent = best_text_to_intent
        
        return best_metric, best_report

    def verify_intents(self, intents):
        """
        Provides a verification of whether the intents of interest are supported by the parser.
        """
        return True

    def _speech_to_text(self, speech):
        # Trying to hit the cache
        # This is 'hacky'
        speech_id = speech.filename_or_fileobject
        if self._cache_speech_to_text:
            if speech_id in self._cached_speech_text:
                return self._cached_speech_text[speech_id]

        # Cache miss *okay*
        with speech as src:
            speech = self.speech_rec.record(src)

        recognized_text = self.speech_rec.recognize_google(speech, language="ru-RU")
        
        # Cacheeeeee
        self._cached_speech_text[speech_id] = recognized_text

        return recognized_text


class TextToIntentSimple:
    def __init__(self, intent_max_distance=3, slot_max_distance=19):
        self._morph               = pymorphy2.MorphAnalyzer()
        self._intent_max_distance = intent_max_distance
        self._slot_max_distance   = slot_max_distance

    def parse(self, text, intents):
        # Parse intent
        intent = self._get_most_similar_entity(text, 
            intents, 
            keywords=[intent.get_keywords() for intent in intents],
            unknown_dist=self._intent_max_distance,
            unknown=None)
        
        # Could not identify the intent
        if intent is None:
            return None
            
        # Parse slot (No support for intents with more than one slot)
        if len(intent.get_slots()) == 1:
            slot_type   = intent.get_slots()[0]
            slot_values = slot_type.get_values()
            slot = self._get_most_similar_entity(text, 
                slot_values, 
                keywords=[slot_type.get_keywords_by_value(value) for value in slot_values],
                unknown_dist=self._slot_max_distance,
                unknown=None)
            return intent([slot_type(slot)])
        else:
            return intent()

    def _get_most_similar_entity(self, text, entities, keywords, unknown_dist, unknown):
        """
        Every entity is paired with its list of keywords.
        entities = [...]
        keywords = [[], [], ...]
        """
        text  = text.translate(str.maketrans('', '', string.punctuation))
        words = text.split(" ")
        words = [self._morph.parse(word)[0].normal_form for word in words]
        min_dist = 10000000
        min_entity = None
        for keywords, entity in zip(keywords, entities):
            # Skip empty entities
            if len(keywords) == 0:
                continue
            keywords = [self._morph.parse(keyword)[0].normal_form for keyword in keywords]
            entity_distance = 0
            for word in words:
                word = self._morph.parse(word)[0].normal_form
                entity_distance = min([editdistance.distance(word, keyword) for keyword in keywords])

                if entity_distance < min_dist:
                    min_entity = entity
                    min_dist = entity_distance

        if min_dist < unknown_dist:
            return min_entity
        else:
            return unknown
