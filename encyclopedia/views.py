from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django import forms

from . import util
import random

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def wiki(request, title):
    entry = util.get_entry(title)
    if entry == None:
        return render(request, "encyclopedia/error.html", {
            "error": "ERROR SITE NOT FOUND"
        })
    
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": util.md_to_html(entry),
    })

def search(request):
    q = request.POST.__getitem__("q")
    q_upper = q.upper()

    entries = util.list_entries()
    entries_upper = [x.upper() for x in entries]
    if q_upper in entries_upper:
        return HttpResponseRedirect(reverse("encyclopedia:title", args=(q,)))
    else:
        suggestions = list()
        for index, entry in enumerate(entries_upper):
            if entry.find(q_upper) != -1:
                suggestions.append(entries[index])
            continue
        return render(request, "encyclopedia/search-results.html", {
            "q": q,
            "suggestions": suggestions,
        })

class NewPageForm(forms.Form):
    name = forms.CharField(label="entry name", max_length=32)
    content = forms.CharField(widget=forms.Textarea(attrs={"rows": 10, "cols": 128}))

class EditPageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={"rows": 10, "cols": 128}))




def new_page(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            name = name.capitalize()

            if util.get_entry(name):
                return render(request, "encyclopedia/new-page.html", {
                    "form": form,
                    "error": "Error! Entry already exists."
                })
            else:
                util.save_entry(name, form.cleaned_data["content"])
                return HttpResponseRedirect(reverse("encyclopedia:title", args=(name,)))

    return render(request, "encyclopedia/new-page.html", {
        "form": NewPageForm()
    })


def random_page(request):
    rand = random.choice(util.list_entries())
    return HttpResponseRedirect(reverse("encyclopedia:title", args=(rand,)))



def edit_page(request, title):
    title.capitalize()
    title_upper = title.upper()

    entries = util.list_entries()
    entries_upper = [x.upper() for x in entries]
    if not title_upper in entries_upper:
        return render(request, "encyclopedia/error.html", {
            "error": "ERROR SITE NOT FOUND"
        })
    
    if request.method == "GET":
        entry = util.get_entry(title)
        form = EditPageForm(initial={
            "content": entry,
            })
        
        return render(request, "encyclopedia/edit-page.html", {
            "form": form,
            "name": title
        })
    
    if request.method == "POST":
        form = EditPageForm(request.POST)
        if form.is_valid():

            util.save_entry(title, form.cleaned_data["content"])
            return HttpResponseRedirect(reverse("encyclopedia:title", args=(title,)))


        