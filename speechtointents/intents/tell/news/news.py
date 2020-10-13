from speechtointents.intents.intent import Intent

class News(Intent):
    KEYWORD = "news"

    @staticmethod
    def help_text():
        return "новости"

    @staticmethod
    def get_keywords():
        return ["новости"]

    @staticmethod
    def get_phrases():
        return ["что в мире происходит?", "что на повестке дня?"]