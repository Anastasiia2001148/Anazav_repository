from django.shortcuts import render, redirect, get_object_or_404
from .utils import get_mongodb
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .forms import AuthorForm, QuoteForm
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, View
from .models import Quote, Author,Tag
from django.http import Http404


def main(request, page=1):
    quotes = Quote.objects.select_related('author').all()  # Загружаем цитаты вместе с авторами
    per_page = 10
    paginator = Paginator(quotes, per_page)
    try:
        quotes_on_page = paginator.page(page)
    except:
        raise Http404("Page not found")

    return render(request, 'quotes/index.html', context={'quotes': quotes_on_page})

@method_decorator(login_required, name='dispatch')
class AddAuthorView(View):
    template_name = 'quotes/add_author.html'

    def get(self, request):
        form = AuthorForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('quotes:quote_list')
        return render(request, self.template_name, {'form': form})

@method_decorator(login_required, name='dispatch')
class AddQuoteView(View):
    template_name = 'quotes/add_quote.html'

    def get(self, request):
        form = QuoteForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = QuoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('quotes:quote_list')
        return render(request, self.template_name, {'form': form})

class QuoteListView(View):
    template_name = 'quotes/quote_list.html'
    context_object_name = 'quotes'

    def get(self, request):
        search_query = request.GET.get('search', '')
        quotes = Quote.objects.select_related('author')

        if search_query:
            quotes = quotes.filter(quote__icontains=search_query)

        return render(request, self.template_name, {'quotes': quotes, 'search_query': search_query})


def author_detail_view(request, pk):
    author = get_object_or_404(Author, pk=pk)
    return render(request, 'quotes/author_detail.html', {'author': author})


def tag_view(request,tag_name):
    tag = get_object_or_404(Tag, name= tag_name)
    quotes= tag.quote_set.all()
    return render(request, 'quotes/tag_detail.html', {'tag':tag, 'quotes': quotes})

