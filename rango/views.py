from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import  RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

#import category model
from rango.models import Category
from rango.models import Page

#using forms
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm
def index(request):
    # Request the context of the request.
    # The context contains information such as the client's machine details, for example.
    context = RequestContext(request)
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by no. likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-likes')[:5]
    # Construct a dictionary to pass to the template engine as its context.
# Place the list in our context_dict dictionary which will be passed to the template engine.
    context_dict = {'categories': category_list,'pages':page_list}
    
    #for category in category_list:
    # category.url = category.name.replace(' ','_')
    category.url= encode_url(category_list)    
    # Return a rendered response to send to the client.
    return render_to_response('rango/index.html',context_dict,context)

def about(request):
    context = RequestContext(request)
    context_dict ={'boldmessage':'rock and roolll'}
    return render_to_response('rango/about.html',context_dict,context)
    
    return HttpResponse("Rango says Here is the about page <a href='/rango/'>Index</a>")

def category(request,category_name_url):
    context = RequestContext(request)
    # Change underscores in the category name to spaces.
    # URLs don't handle spaces well, so we encode them as underscores.
    # We can then simply replace the underscores with spaces again to get the name.
    #category_name = category_name_url.replace('_', ' ')
    category_name =decode_url(category_name_url)
# Create a context dictionary which we can pass to the template rendering engine.
    # We start by containing the name of the category passed by the user.
    context_dict = {'category_name': category_name}
    try:
        # Can we find a category with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(name=category_name)
        
        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category)
        
        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
         
        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] =category
        context_dict['category_name_url']=category_name_url
    except Category.DoesNotExist:
                # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass
    
        #Go render the response and return it to the client.
    return render_to_response('rango/category.html',context_dict,context)

def encode_url(category_list):
    for category in category_list:
        category.url = category.name.replace(' ','_')
    return category.url

def decode_url(category_name_url):
    category_name = category_name_url.replace('_', ' ')
    return category_name

def add_category(request):
    context = RequestContext(request)
    
    #A HTTP POST
    if request.method =='POST':
        form = CategoryForm(request.POST)
        
        #have we been provided a valid form?
        if form.is_valid():
            form.save(commit=True)
        
        #now call the index() view
        #user will be shown next homepage
            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm #display the form to enter detail
    return render_to_response('rango/add_category.html',{'form':form},context)

def add_page(request,category_name_url):
    context = RequestContext(request)
    
    category_name = decode_url(category_name_url)
    if request.method =='POST':
        form = PageForm(request.POST)
        
        if form.is_valid():
            # This time we cannot commit straight away.
            # Not all fields are automatically populated!
            page = form.save(commit = False)
            
            #Retrieve the associated Category object so we can add it.
            # Wrap the code in a try block - check if the category actually exists!
            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                # If we get here, the category does not exist.
                # Go back and render the add category form as a way of saying the category does not exist.
                return render_to_response('rango/add_category.html',{}, context)
            
            page.views = 0
            page.save()
            
            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()
    
    return render_to_response('rango/add_page.html',
                              {'category_name_url': category_name_url,
                               'category_name': category_name,
                               'form': form},
                              context)
                
def register(request):
    context = RequestContext(request)
        # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds
    registered= False
        # If it's a HTTP POST, we're interested in processing form data.
    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        # Note that we make use of both UserForm and UserProfileForm.
        user_form = UserForm(data=request.POST)
        profile_form =UserProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()
            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()
            # Now sort out the UserProfile instance.
            # Since we need to set the user attribute ourselves, we set commit=False.
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user
            # Did the user provide a profile picture?
            # If so, we need to get it from the input form and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            
            profile.save()
            registered = True
        else:
            print user_form.errors, profile_form.errors
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
        
    return render_to_response('rango/register.html',{'user_form': user_form, 'profile_form': profile_form, 'registered':registered},context)
            
def user_login(request):
    context= RequestContext(request)
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username = username , password = password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse("Your Rango account is disabled")
        else:
            print "Invalid login details {0}, {1}".format(username, password)
            return HttpResponse("Invalid login details supplied.")
    else:
        return render_to_response('rango/login.html', {}, context)

@login_required #decorator
def restricted(request):
    return HttpResponse("Since you are logged in, you can see this text")    

@login_required
def user_logout(request):
    logout(request)
    
    return HttpResponseRedirect('/rango/')