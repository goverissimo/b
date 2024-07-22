from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from django.contrib import messages
from django.urls import reverse
from .models import AvailabilitySlot, AppointmentDuration
from .forms import AppointmentDurationForm
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def admin_required(view_func):
    def check_admin(user):
        if user.is_staff or user.is_superuser:
            return True
        raise PermissionDenied
    return user_passes_test(check_admin)(view_func)


@admin_required
def availability_settings(request):
    """
    View for managing availability settings and appointment duration.
    """
    AvailabilityFormSet = modelformset_factory(
        AvailabilitySlot,
        fields=('day_of_week', 'start_time', 'end_time'),
        extra=1,
        can_delete=True
    )
    
    # Get or create the AppointmentDuration instance
    appointment_duration, created = AppointmentDuration.objects.get_or_create(
        pk=1,
        defaults={'duration': 30}
    )
    
    if request.method == 'POST':
        if 'duration' in request.POST:
            duration_form = AppointmentDurationForm(request.POST, instance=appointment_duration)
            if duration_form.is_valid():
                duration_form.save()
                messages.success(request, 'Appointment duration updated successfully.')
            else:
                messages.error(request, 'Error updating appointment duration.')
        elif 'form-TOTAL_FORMS' in request.POST:
            formset = AvailabilityFormSet(request.POST)
            if formset.is_valid():
                instances = formset.save(commit=False)
                for obj in formset.deleted_objects:
                    obj.delete()
                for instance in instances:
                    instance.save()
                formset.save_m2m()
                messages.success(request, 'Availability settings updated successfully.')
            else:
                messages.error(request, 'Error updating availability settings.')
        
        return redirect(reverse('availability:availability-settings'))
    
    formset = AvailabilityFormSet(queryset=AvailabilitySlot.objects.all())
    duration_form = AppointmentDurationForm(instance=appointment_duration)

    return render(request, 'availability/availability_settings.html', {
        'availability_formset': formset,
        'duration_form': duration_form,
    })