from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Episode

@login_required
@require_GET
def episode_details_api(request, episode_id):
    """API endpoint to get full episode details for the modal view"""
    episode = get_object_or_404(Episode, custom_id=episode_id)
    
    # Format the episode data for JSON response
    data = {
        'custom_id': episode.custom_id,
        'title': episode.title,
        'episode_number': episode.episode_number,
        'description': episode.description or '',
        'created_at': episode.created_at.isoformat(),
        'updated_at': episode.updated_at.isoformat(),
        'ai_summary': episode.ai_summary or '',
        'ai_topics': episode.ai_topics or [],
        'ai_age_rating': episode.ai_age_rating or '',
        'duration_timecode': episode.duration_timecode or '',
        'schedule_count': episode.schedule_count or 0,
        'last_scheduled': episode.last_scheduled.isoformat() if episode.last_scheduled else None,
        'program': {
            'custom_id': episode.program.custom_id,
            'program_name': episode.program.program_name,
            'creator': {
                'custom_id': episode.program.creator.custom_id,
                'first_name': episode.program.creator.first_name,
                'last_name': episode.program.creator.last_name,
                'channel_name': episode.program.creator.channel_name,
            }
        }
    }
    
    return JsonResponse(data)