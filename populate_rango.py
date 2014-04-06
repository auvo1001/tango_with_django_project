import os

def populate():
    #add new category Python with associated pages
    python_cat = add_cat('Python',128,64)
    
    add_page(cat=python_cat,
             title = "Official Python Tutorial",
             url = "http://docs.python.org/2/tutorial",2)
    
    add_page(cat=python_cat,
             title = "How to think like a Copmputer Scientist",
             url = "http://www.greenteapress.ncom/thinkpython/",5)
    
    add_page(cat=python_cat,
             title = "Learn Python in 10 minutes",
             url = "http://www.korokithakis.net/tutorials/python",7)
    
    #add new category Django with associated pages
    django_cat = add_cat("Django",64,32)
    
    add_page(cat=django_cat,
        title="Official Django Tutorial",
        url="https://docs.djangoproject.com/en/1.5/intro/tutorial01/",1)

    add_page(cat=django_cat,
        title="Django Rocks",
        url="http://www.djangorocks.com/",2)

    add_page(cat=django_cat,
        title="How to Tango with Django",
        url="http://www.tangowithdjango.com/",3)

#add new category other frameworks with associated pages
    frame_cat = add_cat("Other Frameworks",32,16)

    add_page(cat=frame_cat,
        title="Bottle",
        url="http://bottlepy.org/docs/dev/",3)

    add_page(cat=frame_cat,
        title="Flask",
        url="http://flask.pocoo.org",1)
    
    #print out what we have added
    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print "-{0} - {1}".format(str(c),str(p))
            
def add_page(cat,title,url,views=0):
    p = Page.objects.get_or_create(category=cat,title=title,url=url,views=views)[0]
    return p

def add_cat(name,views=0,likes=0):
    c = Category.objects.get_or_create(name=name,views=views,likes=likes)[0]
    return c

#start execution
if __name__ =='__main__':
    print "Starting Rango population script..."
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')
    from rango.models import Category, Page
    populate()