from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .forms import ClientForm
from .models import Client
from django.views.decorators.http import require_POST
def client_list(request):
    clients = Client.objects.all()
    return render(request, 'clients/client_list.html', {'clients': clients})

def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        telegram_id = request.POST.get('telegram_id')
        print(f"Received POST request with telegram_id: {telegram_id}")
        print(f"Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        if form.is_valid():
            client = form.save(commit=False)
            client.telegram_id = telegram_id
            client.save()
            return redirect(reverse('clients:client-list'))
        else:
            print("Form is invalid, not redirecting")
    else:
        form = ClientForm()
    return render(request, 'clients/client_create.html', {'form': form})

def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    print("page")
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        print(f"Received POST request for client update, pk: {pk}")
        print(f"Form is valid: {form.is_valid()}")
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        if form.is_valid():
            form.save()
            return redirect(reverse('clients:client-list'))
    else:
        form = ClientForm(instance=client)
    return render(request, 'clients/client_form.html', {'form': form, 'object': client})