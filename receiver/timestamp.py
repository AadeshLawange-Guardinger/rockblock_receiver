from datetime import datetime, timedelta

def convert_to_datetime(timestamp, duration_seconds):
    # Extract the year, month, day, hour, minute, and second from the timestamp
    year = int(timestamp[:4])
    month = int(timestamp[4:6])
    day = int(timestamp[6:8])
    hour = int(timestamp[8:10])
    minute = int(timestamp[10:12])
    second = int(timestamp[12:14])

    # Create a datetime object from the extracted components
    start_datetime = datetime(year, month, day, hour, minute, second)

    # Add the duration to the start datetime
    end_datetime = start_datetime + timedelta(seconds=duration_seconds)

    return end_datetime

def generate_timestamps(start_datetime, num_timestamps, duration_seconds):
    timestamps = [start_datetime + timedelta(seconds=i) for i in range(num_timestamps)]
    return timestamps

def timestamp_list(header_timestamp):
    timestamp = header_timestamp
    duration_seconds = int(timestamp[-4:])  # Extract last four digits as seconds

    # Remove last four digits from timestamp
    timestamp = timestamp[:-4]

    # Convert to datetime
    end_datetime = convert_to_datetime(timestamp, duration_seconds)

    # Generate additional timestamps
    num_timestamps = 5  # Number of additional timestamps to generate

    timestamps = generate_timestamps(end_datetime, num_timestamps, 1)  # Difference between timestamps is 1 second

    return timestamps