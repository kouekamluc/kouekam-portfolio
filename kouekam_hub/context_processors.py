from portfolio.models import Profile

def profile_context(request):
    """Make profile available in all templates"""
    profile = Profile.objects.first()
    return {
        'profile': profile,
    }

