from django.db.models import Min, Max, Count
import binascii
import json
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from receiver.decompression import process_compressed_data
from receiver.timestamp import timestamp_list
from .models import RockBlockMessage, RockBlockMessage2, UserCredentials
from django.core import serializers
import numpy as np
from django.db.models import Count, Max, Min
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.http import JsonResponse
from django.http import StreamingHttpResponse


################################################# FETCH DATA FROM SATELLITE ###############################################

@api_view(["POST"])
def receive_message_2(request):
    if request.method == 'POST':
        imei = request.POST.get('imei')
        momsn = request.POST.get('momsn')
        transmit_time = request.POST.get('transmit_time')
        iridium_latitude = request.POST.get('iridium_latitude')
        iridium_longitude = request.POST.get('iridium_longitude')
        iridium_cep = request.POST.get('iridium_cep')
        data = request.POST.get('data')

        new_data = hex_decoder(data)
        # print(new_data)

        # Skip the first character if it's a quotation mark
        if new_data.startswith('"'):
            split_new_data = new_data[1:]

        # Validate if the first 18 characters are numbers
        header = split_new_data[:21]
        if not header.isdigit():
            # Get the header of the most recent row in the database
            last_entry = RockBlockMessage2.objects.all().order_by('-id').first()

            doa = last_entry.doa
            
            if last_entry:
                last_header = last_entry.header
            else:
                last_header = ""

            # Use the header from the last entry
            header = last_header
            
            remaining_data = new_data
        else:
            # Split the data into header and remaining data
            remaining_data = '"' + split_new_data[21:]
            doa = header[18:21]

        # Save the received message
        message = RockBlockMessage2.objects.create(
            imei=imei,
            momsn=momsn,
            transmit_time=transmit_time,
            iridium_latitude=iridium_latitude,
            iridium_longitude=iridium_longitude,
            iridium_cep=iridium_cep,
            header=header[:18],
            doa=doa,
            data=remaining_data
        )

        # Respond with success message
        return JsonResponse({'status': 'success'})

    # Respond with error for non-POST requests
    return JsonResponse({'error': 'Invalid request method'}, status=400)


def unescape_unicode(data):
    # Replace double backslashes with single backslashes
    data = data.replace('\\\\', '\\')

    try:
        # Unescape Unicode characters
        data = data.encode().decode('unicode-escape')
    except UnicodeDecodeError as e:
        # Handle the case where decoding fails
        print(f"Unicode decoding error: {e}")
        # You can choose to return an empty string or raise an exception here based on your application's logic
        return ""

    return data


def hex_decoder(hex_string):
    try:
        decoded_bytes = bytes.fromhex(hex_string)
        return decoded_bytes.decode('utf-8')
    except ValueError:
        return "Invalid hex string"

################################################# SHOW DATA ###############################################


@api_view(["POST"])
def get_messages(request):
    request_data = json.loads(request.body)
    momsn_start = request_data.get('momsnStart')
    momsn_end = request_data.get('momsnEnd')

    # print(momsn_start,momsn_end)

    if momsn_start is not None and momsn_end is not None:
        # Retrieve header data where momsn equals momsn_start
        header_data = RockBlockMessage2.objects.filter(
            momsn=momsn_start).values_list('header', flat=True).first()
    else:
        header_data = None

    # print("Timestamp:",header_data)

    # timestamps = timestamp_list(header_data)

    # print(timestamps)

    if momsn_start is not None and momsn_end is not None:

        # Retrieve the report information for momsn_end
        end_report_info = RockBlockMessage2.objects.filter(momsn=momsn_end).values(
            'iridium_latitude', 'iridium_longitude', 'transmit_time', 'doa').first()

        # Parse transmit_time to extract date and time
        transmit_time = end_report_info.get('transmit_time')
        date, time = transmit_time.split(' ')

        # Update end_report_info with latitude, longitude, date, and time
        end_report = {
            'latitude': end_report_info.get('iridium_latitude'),
            'longitude': end_report_info.get('iridium_longitude'),
            'date': date,
            'time': time
        }

        messages = RockBlockMessage2.objects.filter(momsn__range=(
            momsn_start, momsn_end)).order_by('momsn').values_list('data', flat=True)
    else:
        messages = None

    merged_data = ''.join(messages)
    print(merged_data)
    # decoded_data = hex_decoder(merged_data)

    # Write decoded data to JSON file without escaping characters
    # with open('compressed_data.json', 'wb') as json_file:
    #     json_file.write(merged_data.encode('utf-8'))

    # Call the function to process the uncompressed data
    T_stft, F_stft, Zxx_dB_stft, t_waveform, audio_reconstructed_waveform, freqs_psd, psd = process_compressed_data(merged_data)

    # Convert processed data to JSON serializable format
    T_list = T_stft.tolist()
    F_list = F_stft.tolist()
    Zxx_compressed_resized_abs = np.abs(
        Zxx_dB_stft)  # Take absolute values
    Zxx_compressed_resized_list = Zxx_compressed_resized_abs.tolist()

    # Organize data into respective categories
    stft_data = {
        'T': T_list,
        'F': F_list,
        'Zxx_compressed_resized': Zxx_compressed_resized_list
    }

    waveform_data = {
        't_waveform': t_waveform.tolist(),
        'audio_reconstructed_waveform': audio_reconstructed_waveform.tolist()
    }

    psd_data = {
        'freqs_psd': freqs_psd.tolist(),
        'psd': psd.tolist()
    }

    map_data = {
        'lat': end_report_info.get('iridium_latitude'),
        'long': end_report_info.get('iridium_longitude'),
        'doa': str(end_report_info.get('doa')) + '°' if end_report_info.get('doa') is not None else '--N/A--',
    }

    # Combine data into the final response
    response_data = {
        'stft_data': stft_data,
        'waveform_data': waveform_data,
        'psd_data': psd_data,
        'doa': str(end_report_info.get('doa')) + '°' if end_report_info.get('doa') is not None else '--N/A--',
        'report_info': end_report,
        'bouy_id': f"AS-D 6891",
        'packet_id': f"{momsn_start} - {momsn_end}",
        'map_data': map_data
    }
    return JsonResponse(response_data)


def heatmap_view(request):
    return render(request, 'heatmap.html')

################################################# SHOW LATEST PACKET RECEIVED ###############################################


@api_view(["GET"])
def get_latest_message(request):
    try:
        # Retrieve the last row from the table
        last_message = RockBlockMessage2.objects.latest('id')
        # Assuming 'id' is the primary key field, change it to the appropriate field name if needed

        def generate_response():
            # Serialize the last message
            data = serializers.serialize('json', [last_message])
            yield data

        response = StreamingHttpResponse(
            generate_response(), content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="latest_message.json"'
        return response
    except RockBlockMessage2.DoesNotExist:
        # Handle the case where no messages exist in the table
        return JsonResponse({'error': 'No messages found'}, status=404)


################################################# LOGIN ###############################################


@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            # Check if both username and password are provided
            if not (username and password):
                return JsonResponse({'error': 'Both username and password are required'}, status=400)

            # Authenticate user against UserCredentials model
            try:
                user_credentials = UserCredentials.objects.get(
                    username=username, password=password)
            except UserCredentials.DoesNotExist:
                user_credentials = None

            if user_credentials is not None:
                # Login successful
                return JsonResponse({'message': 'Login successful'})
            else:
                # Invalid username or password
                return JsonResponse({'error': 'Invalid username or password'}, status=401)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

################################################# FETCH HISTORY ###############################################


# def fetch_history_2(request):
#     # Retrieve the data and group by header
#     grouped_data = RockBlockMessage2.objects.values('header').annotate(
#         momsn_start=Min('momsn'),
#         momsn_end=Max('momsn'),
#         transmit_start=Min('transmit_time'),
#         transmit_end=Max('transmit_time')
#     ).order_by('-momsn_start')

#     # Calculate total count of MOMSN
#     momsn_count = RockBlockMessage2.objects.aggregate(
#         total_momsn=Count('momsn'))

#     # Create a list to store the grouped data with ranges
#     history_list = []

#     # Iterate over the grouped data
#     for item in grouped_data:
#         momsn_start = item['momsn_start']
#         momsn_end = item['momsn_end']
#         transmit_start = item['transmit_start']
#         transmit_end = item['transmit_end']

#         # Add the data to the history list
#         history_list.append({
#             'momsn_start': momsn_start,
#             'momsn_end': momsn_end,
#             'transmit_start': transmit_start,
#             'transmit_end': transmit_end
#         })

#     # Create the final response dictionary
#     response_data = {
#         'history': history_list,
#         'momsn_count': momsn_count['total_momsn'],
#         'total_msg': len(history_list)
#     }

#     # Return the response as JSON
#     return JsonResponse(response_data)


def fetch_history_2(request):
    # Retrieve the data and group by header
    grouped_data = RockBlockMessage2.objects.values('header').annotate(
        momsn_start=Min('momsn'),
        momsn_end=Max('momsn'),
        transmit_start=Min('transmit_time'),
        transmit_end=Max('transmit_time')
    ).order_by('-momsn_start')

    # Calculate total count of MOMSN
    momsn_count = RockBlockMessage2.objects.aggregate(
        total_momsn=Count('momsn'))

    # Create a list to store the grouped data with ranges
    history_list = []

    # Iterate over the grouped data
    for item in grouped_data:
        momsn_start = item['momsn_start']
        momsn_end = item['momsn_end']
        transmit_start = item['transmit_start']
        transmit_end = item['transmit_end']

        # Retrieve the actual data column at momsn_end
        momsn_end_data = RockBlockMessage2.objects.filter(
            momsn=momsn_end).values_list('data', flat=True).first()
        momsn_start_data = RockBlockMessage2.objects.filter(
            momsn=momsn_start).values_list('data', flat=True).first()

        # Check if momsn_end data ends with a double quote
        if momsn_end_data and momsn_end_data.endswith('"') and momsn_start_data and momsn_start_data.startswith('"'):
            # Append to history_list only if the condition is met
            history_list.append({
                'momsn_start': momsn_start,
                'momsn_end': momsn_end,
                'transmit_start': transmit_start,
                'transmit_end': transmit_end
            })

    # Create the final response dictionary
    response_data = {
        'history': history_list,
        'momsn_count': momsn_count['total_momsn'],
        'total_msg': len(history_list)
    }

    # Return the response as JSON
    return JsonResponse(response_data)


def buoy_list_api(request):
    buoy_ids = []
    prefix = "AS-D 68"

    # Generate buoy IDs from 1 to 96
    for i in range(91, 97):
        buoy_id = f"{prefix}{i}"
        buoy_ids.append({'buoy_id': buoy_id, 'status': 1 if i == 91 else 0})

    # Return the response as JSON
    return JsonResponse({'buoy_data': buoy_ids})



################################################# OLD API'S###############################################

# def fetch_history(request):

#     momsn_count = RockBlockMessage.objects.aggregate(total_momsn=Count('momsn'))
#     # Retrieve data from the database
#     data = RockBlockMessage.objects.filter(
#         momsn__in=[87, 95, 100, 121]).order_by('momsn', 'transmit_time')

#     # Initialize variables
#     momsn_start = None
#     momsn_end = None
#     transmit_start = None
#     transmit_end = None
#     result = []

#     # Iterate through the data
#     for item in data:
#         # Set MOMSN start and transmit start for the current range
#         if item.momsn == 87 or item.momsn == 100:
#             momsn_start = item.momsn
#             transmit_start = item.transmit_time
#         # Set MOMSN end and transmit end for the current range
#         elif item.momsn == 95 or item.momsn == 121:
#             momsn_end = item.momsn
#             transmit_end = item.transmit_time
#             # Append the range to the result list
#             result.append({
#                 'momsn_start': momsn_start,
#                 'momsn_end': momsn_end,
#                 'transmit_start': transmit_start,
#                 'transmit_end': transmit_end,
#             })
#             # Reset variables for the next range
#             momsn_start = None
#             momsn_end = None
#             transmit_start = None
#             transmit_end = None

#     # Serialize the result
#     response_data = {'history': result, 'momsn_count': momsn_count['total_momsn']}

#     # Return the serialized data as JSON response
#     return JsonResponse(response_data)


# @api_view(["POST"])
# def receive_message(request):
#     if request.method == 'POST':
#         imei = request.POST.get('imei')
#         momsn = request.POST.get('momsn')
#         transmit_time = request.POST.get('transmit_time')
#         iridium_latitude = request.POST.get('iridium_latitude')
#         iridium_longitude = request.POST.get('iridium_longitude')
#         iridium_cep = request.POST.get('iridium_cep')
#         data = request.POST.get('data')

#         # Save the received message
#         message = RockBlockMessage.objects.create(
#             imei=imei,
#             momsn=momsn,
#             transmit_time=transmit_time,
#             iridium_latitude=iridium_latitude,
#             iridium_longitude=iridium_longitude,
#             iridium_cep=iridium_cep,
#             data=data
#         )

#         # Respond with success message
#         return JsonResponse({'status': 'success'})

#     # Respond with error for non-POST requests
#     return JsonResponse({'error': 'Invalid request method'}, status=400)


# @api_view(["GET"])
# def get_latest_message(request):
#     try:
#         # Retrieve the last row from the table
#         last_message = RockBlockMessage.objects.latest('id')
#         # Assuming 'id' is the primary key field, change it to the appropriate field name if needed

#         response_data = {
#             'id': last_message.id,
#             'imei': last_message.imei,
#             'momsn': last_message.momsn,
#             'transmit_time': last_message.transmit_time,
#         }

#         return JsonResponse(response_data)
#     except RockBlockMessage.DoesNotExist:
#         # Handle the case where no messages exist in the table
#         return JsonResponse({'error': 'No messages found'}, status=404)
