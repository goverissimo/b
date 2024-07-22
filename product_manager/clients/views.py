from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .forms import ClientForm
from .models import Client
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test

def admin_check(user):
    return user.is_staff or user.is_superuser

@user_passes_test(admin_check)
def client_list(request):
    """
    Display a list of all clients.
    """
    clients = Client.objects.all()
    return render(request, 'clients/client_list.html', {'clients': clients})
@user_passes_test(admin_check)
def client_create(request):
    """
    Create a new client.
    """
    if request.method == 'POST':
        form = ClientForm(request.POST)
        telegram_id = request.POST.get('telegram_id')
        if form.is_valid():
            client = form.save(commit=False)
            client.telegram_id = telegram_id
            client.save()
            messages.success(request, 'Client created successfully.')
            return redirect(reverse('clients:client-list'))
        else:
            messages.error(request, 'There was an error creating the client. Please check the form.')
    else:
        form = ClientForm()
    return render(request, 'clients/client_create.html', {'form': form})


@user_passes_test(admin_check)
def client_update(request, pk):
    """
    Update an existing client.
    """
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client updated successfully.')
            return redirect(reverse('clients:client-list'))
        else:
            messages.error(request, 'There was an error updating the client. Please check the form.')
    else:
        form = ClientForm(instance=client)
    return render(request, 'clients/client_form.html', {'form': form, 'object': client})

@user_passes_test(admin_check)
@require_POST
def client_delete(request, pk):
    """
    Delete a client.
    """
    client = get_object_or_404(Client, pk=pk)
    client.delete()
    messages.success(request, 'Client deleted successfully.')
    return redirect(reverse('clients:client-list'))