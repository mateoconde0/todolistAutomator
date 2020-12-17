import time


class DateUtils:
    @staticmethod
    def get_week(time_struct=time.localtime()):
        return time.strftime("%U", time_struct)

    @staticmethod
    def get_date():
        return time.strftime("%Y-%m-%d", time.localtime())

    @staticmethod
    def get_time_zone():
        return time.strftime("%Z", time.localtime())

    @staticmethod
    def date_to_string(date):
        return time.strftime("%Y-%m-%d", date)

    @staticmethod
    def string_to_date(sDate):
        try:
            return time.strptime(sDate, "%Y-%m-%d")
        except ValueError as VE:
            try:
                return time.strptime(sDate, "%m-%d-%Y")
            except ValueError:
                try:
                    return time.strptime(sDate, "%d-%m-%Y")
                except ValueError:
                    raise ValueError("Problem parsing date. Please use yyyy-mm-dd")
