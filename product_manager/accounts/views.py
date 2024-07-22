from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.urls import reverse

@require_http_methods(["GET", "POST"])
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_partner:
                return JsonResponse({'success': True, 'redirect': reverse('partners:dashboard')})
            else:
                return JsonResponse({'success': True, 'redirect': reverse('dashboard')})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=400)
    return render(request, 'accounts/login.html')