import pytz
from timezone_field import TimeZoneField


class USTimeZoneField(TimeZoneField):
    CHOICES = [
        (pytz.timezone(tz), tz.replace("_", " ")) for tz in pytz.country_timezones("US")
    ]
