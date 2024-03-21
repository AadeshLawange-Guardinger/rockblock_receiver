import binascii
from django.http import JsonResponse
from rest_framework.decorators import api_view

from receiver.decompression import process_compressed_data
from .models import RockBlockMessage
from django.core import serializers


@api_view(["POST"])
def receive_message(request):
    if request.method == 'POST':
        imei = request.POST.get('imei')
        momsn = request.POST.get('momsn')
        transmit_time = request.POST.get('transmit_time')
        iridium_latitude = request.POST.get('iridium_latitude')
        iridium_longitude = request.POST.get('iridium_longitude')
        iridium_cep = request.POST.get('iridium_cep')
        data = request.POST.get('data')

        # Save the received message
        message = RockBlockMessage.objects.create(
            imei=imei,
            momsn=momsn,
            transmit_time=transmit_time,
            iridium_latitude=iridium_latitude,
            iridium_longitude=iridium_longitude,
            iridium_cep=iridium_cep,
            data=data
        )

        # Respond with success message
        return JsonResponse({'status': 'success'})

    # Respond with error for non-POST requests
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def unescape_unicode(data):
    # Replace double backslashes with single backslashes
    data = data.replace('\\\\', '\\')

    # Unescape Unicode characters
    data = data.encode().decode('unicode-escape')

    return data

def hex_decoder(hex_string):
    try:
        decoded_bytes = bytes.fromhex(hex_string)
        return decoded_bytes.decode('utf-8')
    except ValueError:
        return "Invalid hex string"

@api_view(["GET"])
def get_messages(request):
    messages = RockBlockMessage.objects.all().values_list('data', flat=True)
    merged_data = ''.join(messages)
    decoded_data = hex_decoder(merged_data)
    unescaped_data = unescape_unicode(decoded_data)

    # Call the function to process the uncompressed data
    T, F, Zxx_compressed_resized = process_compressed_data(unescaped_data)

    # Convert processed data to JSON serializable format
    T_list = T.tolist()
    F_list = F.tolist()
    Zxx_compressed_resized_list = Zxx_compressed_resized.tolist()

    # Send the processed data in the JSON response
    response_data = {
        'decoded_data': unescaped_data,
        'T': T_list,
        'F': F_list,
        'Zxx_compressed_resized': Zxx_compressed_resized_list
    }

    return JsonResponse(response_data)

