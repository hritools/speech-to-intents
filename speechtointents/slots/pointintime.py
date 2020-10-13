class PointInTime:
    TODAY = "today"
    TOMORROW = "tomorrow"
    YESTERDAY = "yesterday"
    UNKNOWN = "unknown"

    def __init__(self, value):
        if value not in PointInTime.get_values():
            self.value = PointInTime.UNKNOWN
        else:
            self.value = value

    @staticmethod
    def get_values():
        return [PointInTime.TODAY, PointInTime.YESTERDAY, PointInTime.TOMORROW, PointInTime.UNKNOWN]

    @staticmethod
    def get_keywords_by_value(value):
        if value == PointInTime.TODAY:
            return ["сегодня", "тудей", "сейчас"]
        elif value == PointInTime.YESTERDAY:
            return ["вчера"]
        elif value == PointInTime.TOMORROW:
            return ["завтра"]
        elif value == PointInTime.UNKNOWN:
            return []
        else:
            return []

    @staticmethod
    def get_regexes_by_value(value):
        return []