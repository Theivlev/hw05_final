from django.core.paginator import Paginator


def get_pages_paginator(request, list, pages):
    paginator = Paginator(list, pages)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
