from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import VideoMenschen


@login_required(login_url='/login/')
def menschen_video(request):
    class_level = request.GET.get('class_level', None)
    video_resources = VideoMenschen.objects.filter(video__class_level=class_level) if class_level else None

    context = {
        'video_resources': video_resources,
    }

    return render(request, 'video_menschen.html', context)


@login_required(login_url='/login/')
def videos_view(request):
    return render(request, 'video_landing.html', {})
