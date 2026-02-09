from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from meals.models import Meal, Category
from restaurants.models import Restaurant
from superadmin.models import Complaint
from .forms import ComplaintForm
from django.core.paginator import Paginator


class HomeView(TemplateView):
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_meals'] = Meal.objects.filter(is_available=True)[:8]
        context['categories'] = Category.objects.all()[:6]
        context['restaurants'] = Restaurant.objects.filter(is_active=True)[:6]
        return context


class SearchView(TemplateView):
    template_name = 'core/search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '')
        category_id = self.request.GET.get('category', '')
        min_price = self.request.GET.get('min_price', '')
        max_price = self.request.GET.get('max_price', '')
        
        meals = Meal.objects.filter(is_available=True)
        
        if query:
            meals = meals.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) |
                Q(restaurant__name__icontains=query)
            )
        
        if category_id:
            meals = meals.filter(category_id=category_id)
        
        if min_price:
            meals = meals.filter(price__gte=min_price)
        
        if max_price:
            meals = meals.filter(price__lte=max_price)
        
        # Pagination
        paginator = Paginator(meals, 12)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context.update({
            'meals': page_obj,
            'query': query,
            'categories': Category.objects.all(),
            'selected_category': category_id,
            'min_price': min_price,
            'max_price': max_price,
        })
        return context


class PrivacyPolicyView(TemplateView):
    template_name = 'core/privacy_policy.html'


class TermsOfServiceView(TemplateView):
    template_name = 'core/terms_of_service.html'


class SubmitComplaintView(LoginRequiredMixin, CreateView):
    model = Complaint
    form_class = ComplaintForm
    template_name = 'core/submit_complaint.html'
    success_url = reverse_lazy('core:my_complaints')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Your complaint has been submitted successfully. We will review it shortly.')
        return super().form_valid(form)


class MyComplaintsView(LoginRequiredMixin, ListView):
    model = Complaint
    template_name = 'core/my_complaints.html'
    context_object_name = 'complaints'
    paginate_by = 10
    
    def get_queryset(self):
        return Complaint.objects.filter(user=self.request.user).order_by('-created_at')
