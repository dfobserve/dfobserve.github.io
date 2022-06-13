class Error(Exception):
    """Base class for other exceptions"""

    pass


class TargetNotFoundError(Error):
    """raised when target not in skyx database"""

    pass


class UnknownError(Error):
    """raised when an unknown error has occured"""

    pass


class UnknownCommunicationError(Error):
    """Raised when an unknown error occurs while communicating with a server"""

    pass


class AstropyNameError(Error):
    """raised when a name is not recognized by astropy"""

    pass


class TargetNotUpError(Error):
    """raised when the target is not up at the requested start time"""

    pass


class EndOfNightError(Error):
    """raised when start time calculated is close to the end of the night."""

    pass


class FilterNotRecognizedError(Error):
    """raised when a filter tilt is entered for a filter name not recognized"""

    pass


class TargetUptimeError(Error):
    """raised when the object uptime is less than requested observing plan time"""

    pass


class DayTimeError(Error):
    """raises when the requested start time is before sunset."""

    pass
