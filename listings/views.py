from django.shortcuts import render

# Create your views here.
def home(request):
    # This view renders the home page of the listings app
    return render(request, 'home.html')

def listing(request, listing_id):
    # This view renders the detail page for a specific listing
    # The listing_id parameter is used to retrieve the specific listing from the database
    return render(request, 'listing.html', {'listing_id': listing_id})