from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
import markdown2
import random

from . import util

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    content = util.get_entry(title)
    if content is None:
        return render(request, "encyclopedia/error.html", {
            "message": "A página solicitada não foi encontrada."
        }, status=404)
    
    html_content = markdown2.markdown(content)
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": html_content
    })

def search(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return redirect("index")
        
    if util.get_entry(query):
        return redirect("entry", title=query)
        
    all_entries = util.list_entries()
    results = [entry for entry in all_entries if query.lower() in entry.lower()]
    
    return render(request, "encyclopedia/search.html", {
        "query": query,
        "results": results
    })

def new_page(request):
    if request.method == "POST":
        title = request.POST.get("title").strip()
        content = request.POST.get("content").strip()
        
        # Valida se já existe uma página com esse título
        if util.get_entry(title):
            return render(request, "encyclopedia/new.html", {
                "error": "Já existe uma página com este título!",
                "title": title,
                "content": content
            })
            
        util.save_entry(title, content)
        return redirect("entry", title=title)
        
    return render(request, "encyclopedia/new.html")

def edit_page(request, title):
    if request.method == "POST":
        content = request.POST.get("content").strip()
        util.save_entry(title, content)
        return redirect("entry", title=title)
        
    content = util.get_entry(title)
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": content
    })

def random_page(request):
    entries = util.list_entries()
    if entries:
        random_title = random.choice(entries)
        return redirect("entry", title=random_title)
    return redirect("index")