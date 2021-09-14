from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm
from .decorators import check_recaptcha


def base(request):
    """
    Count visits to all pages
    """
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    return render(request, 'rango/base.html', context=context_dict)


def index(request):
    """
    Query the database for a list of ALL categories currently stored
    Order the categories by likes in descending order(retrieve the top 5 only)
    """
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list,
                    'pages': page_list}
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    response = render(request, 'rango/index.html', context_dict)
    return response


def about(request):
    """
    Create a context dictionary with message and visits counter
    """
    context_dict = {
        'boldmessage': "This tutorial has been put together by Simon."}
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    return render(request, 'rango/about.html', context=context_dict)


def show_category(request, category_name_slug):
    """
    Create a context dictionary with categories and pages(sorted by views)
    """
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['pages'] = None
        context_dict['category'] = None

    return render(request, 'rango/category.html', context_dict)


def add_category(request):
    """
    Add category to DB via CategoryForm() and check validity of entered data
    before saving in DB
    """
    form = CategoryForm()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)
    return render(request, 'rango/add_category.html', {"form": form})


@check_recaptcha
def add_page(request, category_name_slug):
    """
    Add page to particular category(category_name_slug) via PageForm()
    Check validity of entered data and provide Google reCaptcha checking
    """
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid() and request.recaptcha_is_valid:
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return show_category(request, category_name_slug)
        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)


def get_server_side_cookie(request, cookie, default_val=None):
    """
    Store cookies on the server via session
    """
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    """
    Get the number of visits of the site.
    If the cookie exists -> the value returned is casted to an integer
    If not -> the default value of 1 is used
    """
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request,
                                               'last_visit',
                                               str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7],
                                        '%Y-%m-%d %H:%M:%S')
    # If it's more than a second since the last visit...
    if (datetime.now() - last_visit_time).seconds > 0:
        visits = visits + 1
        request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits


def goto_url(request):
    """
    Take a parametrised HTTP GET request(i.e rango/goto/?page_id=1)
    and update the number of views for the page
    Redirect to the actual URL
    """
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(url=page_id)
                print(page)
                page.views = page.views + 1
                page.save()
                url = page.url
            except Exception:
                pass
    return redirect(url)


@login_required
def like_category(request):
    """
    Examine the request and pick out the category_id and then
    increment the number of likes for that category
    Only for authenticated users
    """
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
    likes = 0
    if cat_id:
        cat = Category.objects.get(id=int(cat_id))
        if cat:
            likes = cat.likes + 1
            cat.likes = likes
            cat.save()
    return HttpResponse(likes)
