from datetime import datetime
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import RockBlockMessage

@api_view(["POST"])
def receive_message(request):
    if request.method == 'POST':
        imei = request.POST.get('imei')
        momsn = request.POST.get('momsn')
        transmit_time_str = request.POST.get('transmit_time')
        iridium_latitude = request.POST.get('iridium_latitude')
        iridium_longitude = request.POST.get('iridium_longitude')
        iridium_cep = request.POST.get('iridium_cep')
        data = request.POST.get('data')

        try:
            # Parse transmit_time string to datetime object
            transmit_time = datetime.strptime(transmit_time_str, "%d-%m-%y %H:%M:%S")
            # Format datetime object into the desired format
            transmit_time_formatted = transmit_time.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            # If the format is incorrect, respond with an error
            return JsonResponse({'error': 'Invalid datetime format'}, status=400)

        # Save the received message
        message = RockBlockMessage.objects.create(
            imei=imei,
            momsn=momsn,
            transmit_time=transmit_time_formatted,
            iridium_latitude=iridium_latitude,
            iridium_longitude=iridium_longitude,
            iridium_cep=iridium_cep,
            data=data
        )

        # Respond with success message
        return JsonResponse({'status': 'success'})

    # Respond with error for non-POST requests
    return JsonResponse({'error': 'Invalid request method'}, status=400)
