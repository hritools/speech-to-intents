from speechtointents.intents.intent import Intent

class Joke(Intent):
    KEYWORD = "joke"

    @staticmethod
    def get_keywords():
        return ["шутка", "прикол", "анекдот", "анек"]

    @staticmethod
    def get_slots():
        return []