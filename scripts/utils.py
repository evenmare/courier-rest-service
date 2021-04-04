import datetime
from dateutil import parser


def valitime(text):
    try:
        datetime.datetime.strptime(text, '%H:%M')
    except ValueError:
        raise ValueError

    return text


def validatetime(text):
    return parser.parse(text)


def sublist(lst1, lst2):
    ls1 = [element for element in lst1 if element in lst2]
    ls2 = [element for element in lst2 if element in lst1]
    return ls1 == ls2
