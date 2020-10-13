import speech_recognition as sr

from speechtointents.speechtointents   import SpeechToIntents
from speechtointents.intents.tell      import Joke, Weather, WhatYouCan
from speechtointents.slots.pointintime import PointInTime

# This is how we create speech to intents parser
# SpeechToIntents will choose a concrete solution based on the passed intents
speech_to_intents = SpeechToIntents(intents=[Joke, Weather, WhatYouCan])

# An example of how to parse an audio file
#input_speech = sr.AudioFile("test.wav")
#intent       = speech_to_intents.parse(input_speech)

# An example of how to validate current solution when you have a dataset for validation
import pandas as pd
import os

data           = pd.read_csv("dataset/ours/description.csv")
dataset = []
for row in data.iterrows():
    record = row[1]
    dataset.append((sr.AudioFile(os.path.join("dataset", "ours", record["filename"])), record["intent_keyword"], record["slot_value"]))

# Validation before fitting
validation_scores = speech_to_intents.validate(dataset)
print("Validation report before fitting for our dataset")
print(validation_scores)

# Fit the solution for our dataset
best_score, best_report  = speech_to_intents.fit(dataset)
print("The best score we got (F1-Score): {}".format(best_score))

# Validation after fitting
validation_scores = speech_to_intents.validate(dataset)
print("Validation report after fitting for current solution")
print(validation_scores)