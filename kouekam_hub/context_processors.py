from portfolio.models import Profile

def profile_context(request):
    """Make profile available in all templates"""
    try:
        profile = Profile.objects.first()
    except Exception:
        # If there's any error (e.g., database not ready), return None
        profile = None
    return {
        'profile': profile,
    }

