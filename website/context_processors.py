from .models import OwnerProfile

def owner_profile(request):
    profile = OwnerProfile.objects.first()
    return {
        "profile":profile
    }