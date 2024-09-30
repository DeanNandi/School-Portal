from django import template
from decimal import Decimal

register = template.Library()


@register.filter
def get(value, arg):
    if hasattr(value, 'get'):
        return value.get(arg)
    elif isinstance(value, (list, tuple)) and isinstance(arg, int):
        return value[arg] if 0 <= arg < len(value) else None
    return None


@register.filter
def get_item(obj, key):
    if isinstance(obj, dict):
        return obj.get(key)
    elif isinstance(obj, Decimal):
        return obj
    elif hasattr(obj, key):
        return getattr(obj, key)
    else:
        return None


@register.filter
def get_skill_total(exam, skill):
    return getattr(exam, f'{skill}_total', None)


@register.filter(name='get_by_key')
def get_by_key(d, key):
    """Fetch item from a dictionary by key."""
    return d.get(key)


@register.filter(name='get_attr')
def get_attr(obj, attr):
    """Get an attribute of an object dynamically."""
    return getattr(obj, attr, '')


@register.filter(name='get_skill_score')
def get_skill_score(obj, skill):
    """Get the score for a specific skill."""
    return getattr(obj, f'{skill}_score', '')


@register.filter(name='get_skill_missed_reason')
def get_skill_missed_reason(obj, skill):
    """Get the missed reason for a specific skill."""
    return getattr(obj, f'{skill}_missed_reason', '')


# New filters added for division and multiplication

@register.filter
def div(value, arg):
    """
    Divide the value by the argument
    """
    try:
        value = float(value)
        arg = float(arg)
        if arg == 0:
            return 0  # Return 0 if dividing by zero
        return value / arg
    except (ValueError, TypeError, ZeroDivisionError):
        return 0  # Return 0 for any error (including None values)


@register.filter
def mul(value, arg):
    """
    Multiply the value by the argument
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0  # Return 0 for any error (including None values)


@register.filter
def zip_lists(a, b):
    return zip(a, b)


@register.filter
def gte(value, arg):
    """
    Check if value is greater than or equal to arg
    """
    try:
        return float(value) >= float(arg)
    except (ValueError, TypeError):
        return False


@register.simple_tag
def all_true(*args):
    """
    Check if all arguments are true
    """
    return all(args)


@register.filter
def to_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


@register.filter
def dict_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def multiply(value, arg):
    try:
        return Decimal(value) * Decimal(arg)
    except:
        return 0


@register.filter
def all_subscores_above_60(student_exam):
    skills = ['speaking', 'listening', 'reading', 'writing']
    for skill in skills:
        score = getattr(student_exam, f'{skill}_score', None)
        total = getattr(student_exam, f'{skill}_total', None)
        if score is not None and total is not None:
            if float(score) / float(total) < 0.6:
                return False
        else:
            # If any skill is not entered, we consider it as not passed
            return False
    return True


@register.filter
def exam_passed(student_exam):
    skills = ['speaking', 'listening', 'reading', 'writing']
    any_skill_entered = False
    for skill in skills:
        score = getattr(student_exam, f'{skill}_score', None)
        total = getattr(student_exam, f'{skill}_total', None)
        if score is not None and total is not None:
            any_skill_entered = True
            if float(score) / float(total) < 0.6:
                return False

    # If no skills were entered, check the overall percentage score
    if not any_skill_entered:
        overall_score = getattr(student_exam, 'percentage_score', None)
        if overall_score is not None:
            # Remove '%' sign and convert to float
            try:
                overall_score_float = float(overall_score.rstrip('%'))
                return overall_score_float >= 60.0
            except ValueError:
                return False

    return any_skill_entered  # Return True only if at least one skill was entered and all were above 60%
