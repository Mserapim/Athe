"""Collection of exceptions.
The validation functions of stdnum should raise one of the below exceptions
when validation of the number fails.
"""


class ValidationError(Exception):
    """Top-level error for validating numbers.
    This exception should normally not be raised, only subclasses of this
    exception."""

    def __str__(self):
        return "".join(self.args[:1]) or getattr(self, "message", "")


class InvalidFormat(ValidationError):
    """Something is wrong with the format of the number.
    This generally means characters or delimiters that are not allowed are
    part of the number or required parts are missing."""

    message = "The number has an invalid format."


class InvalidChecksum(ValidationError):
    """The number's internal checksum or check digit does not match."""

    message = "The number's checksum or check digit is invalid."


class InvalidLength(InvalidFormat):
    """The length of the number is wrong."""

    message = "The number has an invalid length."


class InvalidComponent(ValidationError):
    """One of the parts of the number has an invalid reference.
    Some part of the number refers to some external entity like a country
    code, a date or a predefined collection of values. The number contains
    some invalid reference."""

    message = "One of the parts of the number are invalid or unknown."


"""The ISO 7064 Mod 97, 10 algorithm.
The Mod 97, 10 algorithm evaluates the whole number as an integer which is
valid if the number modulo 97 is 1. As such it has two check digits."""


# from stdnum.exceptions import *


def _to_base10(number):
    """Prepare the number to its base10 representation."""
    try:
        return "".join(str(int(x, 36)) for x in number)
    except Exception:
        raise InvalidFormat()


def checksum(number):
    """Calculate the checksum. A valid number should have a checksum of 1."""
    return int(_to_base10(number)) % 97


def calc_check_digits(number):
    """Calculate the extra digits that should be appended to the number to
    make it a valid number."""
    return "%02d" % ((98 - 100 * checksum(number)) % 97)


def validate(number):
    """Check whether the check digit is valid."""
    try:
        valid = checksum(number) == 1
    except Exception:
        raise InvalidFormat()
    if not valid:
        raise InvalidChecksum()
    return number


def is_valid(number):
    """Check whether the check digit is valid."""
    try:
        return bool(validate(number))
    except ValidationError:
        return False
