from django.shortcuts import render, redirect
from django.contrib.auth import login , authenticate , get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import CustemUser , Album,AlbumPhoto, Memory
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.db import transaction
from collections import defaultdict
from collections import defaultdict
from django.http import JsonResponse
import calendar
from django.http import HttpResponseForbidden
from .forms import AlbumEditForm
from django.db.models.functions import ExtractYear
user = get_user_model()

# Create your views here.

def guestuser(request):
    return render(request, 'guestuser.html')

def login_page(request):
    return render(request, 'login.html')

def register_page(request):
    return render(request, 'register.html')

def register_member(request):
    return render(request, 'register_mem.html')

def landing_page(request):
    if request.user.is_authenticated:
        return render(request, 'index.html')
    return render(request, 'guestuser.html')

def member_list(request):
    members = user.objects.filter(profile__role='member')
    return render(request, 'member_list.html', {'members': members})

def register_admin(request):
    if request.method == 'POST':
        full_name = request.POST.get('fullname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        admin_code = request.POST.get('admin_code')

        if password != confirm_password:
            return render(request, 'register_admin.html', {
                'error': 'Passwords do not match'
            })
        
        if user.objects.filter(admin_code=admin_code,is_family_head=True).exists():
            return render(request, 'register_admin.html', {
                'error': 'Admin code already in use. Please choose a different code.'
            })

        user.objects.create(
            fullname=full_name,
            username=username,
            email=email,
            is_family_head=True,
            is_family_member = False ,
            password=make_password(password),
            admin_code=admin_code
        )
        return redirect('user_login')

    return render(request, 'register_admin.html')


#view for register members 

def register_member(request):
    if request.method == 'POST':
        full_name = request.POST.get('fullname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        gender = request.POST.get('gender')
        relationship_to_admin = request.POST.get('relationship')
        admin_code = request.POST.get('admin_code')
        member_id = request.POST.get('member_id')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return render(request, 'register_mem.html', {
                'error': 'Passwords do not match'
            })

        # find the admin with this code
        admin_user= user.objects.filter(admin_code=admin_code , is_family_head=True).first()
        if not admin_user :
            return render(request, "register_mem.html",{'error': 'Invalid admin code '})

        user.objects.create(
            fullname=full_name,
            username=username,
            email=email,
            gender=gender,
            password=make_password(password),
            relationship_to_admin=relationship_to_admin,
            admin_code=admin_code,
            member_id=member_id,
            is_family_member=True,
            is_family_head= False,
            family_head=admin_user  # link to admin
        )

        return redirect('user_login')

    return render(request, 'register_mem.html')

# for all member list ----

@login_required(login_url='guestuser')
@never_cache
def index(request):
    current_user = request.user
    family_code = current_user.admin_code

    # all users in the same family, admin first
    members = user.objects.filter(admin_code=family_code).order_by('-is_family_head')

    admin_code = current_user.admin_code if current_user.is_family_head else None

    # Albums created by the current user
    created_albums = Album.objects.filter(created_by=current_user)

    # Albums explicitly shared with the current user
    shared_albums = Album.objects.filter(shared_with=current_user)

     # Fetch memories of current user (or you can filter by family if needed)
    memories = Memory.objects.filter(user=current_user).order_by('-id')  # latest first

    # Albums shared with the whole family (same family code)
    family_albums = Album.objects.filter(
        share_family=True,
        created_by__admin_code=family_code
    ).exclude(created_by=current_user)  # exclude own albums (already in created_albums)

    # Union of all albums
    albums = (created_albums | shared_albums | family_albums).distinct().order_by('-created_at')    
    return render(request, 'index.html', {
        'user': current_user,
        'members': members,
        'admin_code': admin_code,
        'albums': albums,
        'memories': memories,
    })



# login function with radio button for family head and member
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # your HTML form uses name="agreement" not "is_head"
        agreement = request.POST.get('agreement')  # 'yes' or 'no'

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # optional: check user type against radio button
            if agreement == 'yes' and not user.is_family_head:
                messages.error(request, "You are not authorized as Family Head.")
                return render(request, 'login.html',
                              {'error': 'You are not authorized as Family Head.'})

            if agreement == 'no' and user.is_family_head:
                messages.error(request, "You are not authorized as Family Member.")
                return render(request, 'login.html',
                              {'error': 'You are not authorized as Family Member.'})

            #  actually log the user in
            login(request, user)

            #  redirect to your index (logged-in) page
            return redirect('index')

        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'login.html',
                          {'error': 'Invalid username or password'})

    # GET request just renders the form
    return render(request, 'login.html')


def landing_page(request):
    if request.user.is_authenticated:
        return render(request, 'index.html')
    return render(request, 'guestuser.html')


@never_cache
def log_out(request):
    return redirect(request,'guestuser')

# this is for small page at members details 

def member_details(request, username):
    member = get_object_or_404(CustemUser, username=username)
    # If AJAX, return fragment (no base layout). If normal request, render full page.
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'user_details_pages/member_details.html', {'member': member})
    return render(request, 'member_details.html', {'member': member})

# to delete any user only for admin/head 

def delete_member(request, username):
    if request.method == "POST":
        member = get_object_or_404(CustemUser, username=username)
        
        # Safety check → only allow family head to delete
        if request.user.is_family_head:
            member.delete()
            messages.success(request, f"{member.fullname or member.username} has been deleted.")
        else:
            messages.error(request, "You do not have permission to delete this member.")
        
        return redirect("index")  # change to your list view name

    # If accessed without POST
    return redirect("index")

# view for creating new album 

@login_required(login_url='guestuser')
def create_album(request):
    if request.method == "POST":
        # basic fields
        album_name = request.POST.get("album_name", "").strip()
        description = request.POST.get("description", "").strip()
        cover_photo = request.FILES.get("cover_photo")
        photos = request.FILES.getlist("photos")  # uploaded photos

        # IMPORTANT: correct checkbox handling
        share_family = "share_family" in request.POST  # True only if checkbox was checked

        # gather the raw member ids from the form (may be empty)
        member_ids = request.POST.getlist("members")  # list of strings

        # Only allow sharing with users in the same family as the creator (safety)
        family_code = request.user.admin_code
        family_members_qs = user.objects.filter(admin_code=family_code).exclude(id=request.user.id)

        # Filter submitted member_ids to valid family members (prevents injection/wrong ids)
        if member_ids:
            selected_members_qs = family_members_qs.filter(id__in=member_ids)
        else:
            selected_members_qs = user.objects.none()

        # Save album + relations inside a transaction for safety
        with transaction.atomic():
            album = Album.objects.create(
                name=album_name,
                description=description,
                cover_photo=cover_photo,
                created_by=request.user,
                share_family=share_family
            )

            # Assign shared_with depending on the checkbox or explicit selection
            if share_family:
                # share with entire family (except the creator)
                album.shared_with.set(family_members_qs)
            else:
                # share only with explicitly selected members (or empty)
                album.shared_with.set(selected_members_qs)

            # Save uploaded photos (adjust field name if your model uses 'image' or 'photo')
            for f in photos:
                AlbumPhoto.objects.create(album=album, image=f)

        messages.success(request, "Album created successfully!")
        return redirect("index")

    # GET -> show form
    members = user.objects.filter(admin_code=request.user.admin_code).exclude(id=request.user.id)
    return render(request, "albums_creations/createalbum.html", {"members": members})

# Deleteion of album ---->

@login_required(login_url='guestuser')
def delete_album(request, album_id):
    album = get_object_or_404(Album, id=album_id)

    # Ensure only the creator can delete
    if album.created_by != request.user:
        messages.error(request, "❌ You are not allowed to delete this album.")
        return redirect("index")

    # Delete album → cascades to AlbumPhoto + shared_with
    album.delete()
    messages.success(request, "✅ Album deleted successfully!")
    return redirect("index")

# to delete images from media folder also

@receiver(post_delete, sender=AlbumPhoto)
def delete_photo_file(sender, instance, **kwargs):
    if instance.image: 
        instance.image.delete(False) 

# album details in albumdetails.html 

@login_required(login_url='guestuser')
def album_detail(request, album_id):
    album = get_object_or_404(Album, id=album_id)

    # Ensure only allowed users can view
    if not (
        album.created_by == request.user or
        request.user in album.shared_with.all() or
        (album.share_family and request.user.admin_code == album.created_by.admin_code)
    ):
        messages.error(request, "You do not have permission to view this album.")
        return redirect("index")

    photos = album.photos.all()  # related_name="photos" in AlbumPhoto

    # add family members list (so modal select works)
    # adjust if your user model app is different
    family_members = user.objects.filter(
        admin_code=request.user.admin_code
    )

    return render(request, "albums_creations/albumdetails.html", {
        "album": album,
        "photos": photos,
        "family_members": family_members,   
    })


# album list for each month of year

@login_required(login_url='guestuser')
def album_list(request):
    family_code = request.user.admin_code
    albums = Album.objects.filter(created_by__admin_code=family_code).order_by('-created_at')

    month = request.GET.get('month')
    year = request.GET.get('year')
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]

    if month and year:
        albums = albums.filter(created_at__month=month, created_at__year=year)

    # Group by month
    albums_by_month = defaultdict(list)
    for album in albums:
        month_name = album.created_at.strftime("%B %Y")
        albums_by_month[month_name].append(album)
    albums_grouped = sorted(albums_by_month.items(), reverse=True)

    # Detect AJAX request using header
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "albums_creations/albumlist.html", {
            "albums_grouped": albums_grouped
        })

    return render(request, "albums_creations/albumlist.html", {
        "albums_grouped": albums_grouped,
        "selected_month": month,
        "selected_year": year,
        "months": months,
    })


#edit of albums 

@login_required(login_url='guestuser')
def album_edit(request, album_id):
    album = get_object_or_404(Album, id=album_id)

    # Only album creator or family head can edit
    if not (request.user == album.created_by or request.user.is_family_head):
        messages.error(request, "You are not allowed to edit this album.")
        return redirect("album_detail", album_id=album.id)

    if request.method == "POST":
        name = request.POST.get("name")
        shared_with_ids = request.POST.getlist("shared_with")

        album.name = name
        album.save()

        # Update shared members (convert IDs to integers)
        album.shared_with.set([int(uid) for uid in shared_with_ids])
        messages.success(request, "Album updated successfully!")

        return redirect("album_detail", album_id=album.id)

    return redirect("album_detail", album_id=album.id)

# add photo in album
 
@login_required(login_url='guestuser')
def add_photo_to_album(request, album_id):
    album = get_object_or_404(Album, id=album_id)

    if request.method == "POST":
        image = request.FILES.get("photo")
        if image:
            AlbumPhoto.objects.create(album=album, image=image)
            messages.success(request, "Photo added successfully!")
        else:
            messages.error(request, "Please select an image before submitting.")

    return redirect('album_detail', album_id=album.id)

# view for the memories add, delete etc.

# List all memories of logged-in user
# Add new memory and filter of memories 

@login_required(login_url='guestuser')
def memory_list(request):
    # Handle POST (create new memory)
    if request.method == "POST":
        image = request.FILES.get("image")
        tag = request.POST.get("tag")
        location = request.POST.get("location")

        if image and tag:
            Memory.objects.create(
                user=request.user,
                image=image,
                tag=tag,
                location=location
            )
            messages.success(request, "Memory added successfully!")
            return redirect('memory_list')
        else:
            messages.error(request, "Image and Tag are required!")

    # Handle GET (filtering / listing)
    memories = Memory.objects.filter(user=request.user).order_by('-date')

    # Get filter values from query params
    tag = request.GET.get("tag")
    location = request.GET.get("location")
    date = request.GET.get("date")
    year = request.GET.get("year")

    if tag or location or date or year:
        if tag:
            memories = memories.filter(tag__icontains=tag)
        if location:
            memories = memories.filter(location__icontains=location)
        if date:
            memories = memories.filter(date=date)
        if year:
            memories = memories.filter(date__year=year)
    else:
        # No filters → only 4 recent
        memories = memories[:4]

    return render(request, "memories/memory_list.html", {"memories": memories})


# View single memory (details page)
@login_required(login_url='guestuser')
def memory_detail(request):
    # Group memories by year
    memories = Memory.objects.filter(user=request.user).order_by('-date')
    memories_by_year = {}
    for memory in memories:
        year = memory.date.year if memory.date else "Unknown"
        memories_by_year.setdefault(year, []).append(memory)

    # Fetch all albums of this user
    user_albums = Album.objects.filter(created_by=request.user)

    return render(request, "memories/memory_detail.html", {
        "memories_by_year": memories_by_year,
        "user_albums": user_albums
    })


# Delete memory
@login_required(login_url='guestuser')
def memory_delete(request, memory_id):
    memory = get_object_or_404(Memory, id=memory_id, user=request.user)

    # Ensure only the creator can delete
    if memory.user != request.user:
        messages.error(request, "❌ You are not allowed to delete this memory.")
        return redirect("memory_list")

    memory.delete()
    messages.success(request, "✅ Memory deleted successfully!")
    return redirect("memory_list")

# to add memory into albums 

@login_required(login_url='guestuser')
def add_memory_to_album(request, memory_id):
    memory = get_object_or_404(Memory, id=memory_id, user=request.user)

    if request.method == "POST":
        album_id = request.POST.get("album_id")
        album = get_object_or_404(Album, id=album_id, created_by=request.user)

        # Add memory’s image to AlbumPhoto
        AlbumPhoto.objects.create(album=album, image=memory.image)

        messages.success(request, f"Memory added to album '{album.name}' successfully!")
        return redirect("memory_detail")  # Adjust to your memory detail/list view name

    messages.error(request, "Invalid request")
    return redirect("memory_detail")


# to view the profile sections of the users 

@login_required(login_url='guestuser')
def profile_view(request):
    user = request.user
    # If you have a related Profile model, you can access it like this
    # (assuming you created OneToOne relation with User)
    profile = getattr(user, 'profile', None)
    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'user_details_pages/profile.html', context)

# updating user profile

@login_required(login_url='guestuser')
def update_profile(request):
    user = request.user  # currently logged-in user
    if request.method == 'POST':
        fullname = request.POST.get('name')
        gender = request.POST.get('gender')
        relationship = request.POST.get('relation')
        family_name = request.POST.get('family_name')
        dob = request.POST.get('dob')
        photo = request.FILES.get('photo')

        # Only family head can edit family_name
        if user.is_family_head and family_name:
            user.fullname = family_name

        # Common fields for all users
        if fullname:
            user.name = fullname
        if gender:
            user.gender = gender
        if relationship:
            user.relationship_to_admin = relationship
        if dob:
            user.dob = dob  # if dob exists in your model
        if photo:
            user.profile_pic = photo  # ensure your model has ImageField

        user.save()
        messages.success(request, "Profile updated successfully!")

        return redirect('profile_view')  # replace with your actual profile page route name

    # If GET, just render the page
    return render(request, 'user_details_pages/profile.html', {'user': user})