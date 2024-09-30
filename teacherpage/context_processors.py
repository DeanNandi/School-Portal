from .models import Teacher


def add_teacher_to_context(request):
    teacher = None
    if request.user.is_authenticated:
        try:
            teacher = Teacher.objects.get(user=request.user)
        except Teacher.DoesNotExist:
            teacher = None
    return {'teacher': teacher}
