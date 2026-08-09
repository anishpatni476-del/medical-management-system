from .models import OwnerProfile

def owner_profile(request):
    if request.user.is_authenticated:

        profile, created = OwnerProfile.objects.get_or_create(
            user = request.user
        )
        return {
            "profile":profile
        }
    return {"profile":None}