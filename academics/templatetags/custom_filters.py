from django import template

register = template.Library()


@register.filter
def absence_reason_class(reason):
    reason_classes = {
        'Too Late', 'Too Late',
        'Absent with Excuse', 'Absent with Excuse',
        'Absent without Excuse', 'Absent without Excuse',
    }
    return reason_classes.get(reason, 'reason-other')


@register.filter
def div(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0


# Resume builder
@register.filter
def get_item(list_obj, index):
    try:
        return list_obj[index]
    except:
        return None


@register.filter
def split_lines(text):
    return text.split('\n')


@register.filter
def get_item_two(dictionary, key):
    return dictionary.get(key)
