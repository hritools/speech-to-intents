from speechtointents.intents.intent import Intent

class WhatYouCan(Intent):
    KEYWORD = "whatyoucan"

    @staticmethod
    def get_keywords():
        return ["умеешь", "функционал", "функции"]

    @staticmethod
    def get_slots():
        return []