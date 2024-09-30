from django import template
from academics.models import StudentExam
from decimal import Decimal

register = template.Library()


@register.filter
def get_student_exam(exams, student_id):
    try:
        return exams.get(student_id=student_id)
    except StudentExam.DoesNotExist:
        return None


@register.filter
def percentage(value, total):
    if value is None or total is None or total == 0:
        return 0
    return (Decimal(value) / Decimal(total)) * 100
