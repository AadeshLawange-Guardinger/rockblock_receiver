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

    dummy_data = "x\u009c\u00d5\u00d3M\u008a\u00c2@\u0010@\u00e1\u00ab\u0004\u00d7\"]\u0095N\u00aa\u00ca\u009d\u00d7\u0018\u0091 &\u0010\u00c1?\u00c6a\u0010d\u00ee>\u00e9'\u00ea\u0019\u00dc<B\u00a8\u000f\u009a.\u00fa>\u00db\u009d\u008f\u0097n\u00b7\u00ea\u00f6\u00a7~\u00b6\u00ac\u00d6R\u00b7i^M\u0015\u00aa\u00b4\u00a6\u00996\u00b4\u00a5F\u009dF\u00a9a\rkX\u00c3\u001a\u00d6\u00b0\u00865\u00aca\r\u00ebX\u00c7:\u00d6\u00b1\u008eu\u00acc\u001d\u00ebX\u00c7\u00066\u00b0\u00c1|0\u001f\u00cc\u0007\u00f3\u00c1|\u0094\u00f9\u009c\u0012\u0015\u00aa\u00b4\u00a6\u00996\u00b4\u00a5F\u009db\u0005+X\u00c1\nV\u00b0\u0082\u0015\u00ac`\u0005+X\u00c5*V\u00b1\u008aU\u00acb\u0015\u00ab\u00b6\u0099W\u00af\u00e5\u00fcn\u000fe9iQ\u008e\u00f3\u00c9-\u00d7\u00f3\u00ac\u00f2\u0019\u009fQ\u000e\u009b\u00e2QV\u00b3\u00ea~\u00c6\u00ef\u00e1:\u009e\u000f\u00fd\u00d0w\u00d7q{\u0019\u001e\u000fh\u00dan\u009d\u00cb\u00c8\u00d7\u00ed\u00f6\u00fe\u00af\u00cdt\u0001m\u00de\u00fc\u00fd\u0003g\u00e6\u00ac\u007f"

    # Call the function to process the uncompressed data
    T, F, Zxx_compressed_resized = process_compressed_data(dummy_data)

    # Convert processed data to JSON serializable format
    T_list = T.tolist()
    F_list = F.tolist()
    Zxx_compressed_resized_list = Zxx_compressed_resized.tolist()

    # Send the processed data in the JSON response
    response_data = {
        # 'decoded_data': unescaped_data,
        'T': T_list,
        'F': F_list,
        'Zxx_compressed_resized': Zxx_compressed_resized_list
    }

    return JsonResponse(response_data)
