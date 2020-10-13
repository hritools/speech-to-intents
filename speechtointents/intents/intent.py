class Intent:
    def __init__(self, slots=None):
        self.concrete_slots = slots or []

    @staticmethod
    def help_text():
        return ""
        
    @staticmethod
    def get_dataset():
        raise Exception("This intent does not have an associated dataset.")

    @staticmethod
    def get_keywords():
        return []

    @staticmethod
    def get_phrases():
        return []

    @staticmethod
    def get_regexes():
        return []
        
    @staticmethod
    def get_slots():
        return []