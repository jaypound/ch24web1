import boto3
import environ
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import logging



# Load environment variables
# env = environ.Env()
# environ.Env.read_env()  # This loads variables from your .env file

def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a pre-signed URL to upload a file to S3."""
    # Create an S3 client with credentials from the environment variables
    aws_access_key_id = env('AWS_ACCESS_KEY_ID', default=None)
    aws_secret_access_key = env('AWS_SECRET_ACCESS_KEY', default=None)
    aws_region = env('AWS_REGION', default='us-east-1')  # Optional default region

    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        
        response = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_name,
            },
            ExpiresIn=expiration
        )
        return response
    except (NoCredentialsError, PartialCredentialsError) as e:
        logging.error(f"Credentials error: {e}")
    except Exception as e:
        logging.error(f"Error generating pre-signed URL: {e}")
    return None


# utils.py

def validate_media_info(media_infos):
    unique_errors = set()
    unique_warnings = set()

    # Define media_checks data structure
    media_checks = {
        'General': {
            'max_duration': 3600,  # Maximum duration in seconds (60 minutes)
            'allowed_extensions': ['mp4', 'mov']  # Allowed file extensions
        },
        'Video': {
            'height_checks': [
                {
                    'height_range': (710, 730),
                    'bitrate_range': (5000000, 7500000),
                    'target_height': 720,
                    'bitrate_error_level': 'WARNING'
                },
                {
                    'height_range': (1070, 1090),
                    'bitrate_range': (8000000, 12000000),  # 8–12 Mbps
                    'target_height': 1080,
                    'bitrate_error_level': 'WARNING'
                }
                # Additional height checks can be added here
            ],
            'acceptable_frame_rates': [23.976, 23.98, 29.97, 30],
            'frame_rate_error_level': 'WARNING',
            'height_error_level': 'WARNING'
        },
        'Audio': {
            'bitrate_range': (128000, 320000),  # 128–320 Kbps
            'channels': [1, 2],                 # One or two audio channels
            'sampling_rates': [48000]           # Sampling rate should be 48000 Hz
        }
    }

    for media_info in media_infos:
        metadata = media_info.metadata
        track_type = metadata.get('track_type', None)

        if track_type == 'General':
            # print(f"Checking {track_type} track")
            # Get duration
            duration = metadata.get('duration', None)
            # Convert duration to float
            try:
                duration = float(duration) if duration is not None else None
            except ValueError:
                duration = None

            if duration is not None:
                duration = duration / 1000  # Convert to seconds
                max_duration = media_checks[track_type]['max_duration']
                if duration > max_duration:
                    duration_minutes = duration / 60  # Convert to minutes for display
                    max_duration_minutes = max_duration / 60
                    error_message = (
                        f"The media duration is {duration_minutes:.2f} minutes, which exceeds the maximum allowed duration of "
                        f"{max_duration_minutes} minutes."
                    )
                    unique_errors.add(error_message)
            else:
                error_message = "Media duration is missing."
                unique_errors.add(error_message)

            # Get file extension
            file_extension = metadata.get('file_extension', None)
            if file_extension is not None:
                allowed_extensions = media_checks[track_type]['allowed_extensions']
                if file_extension not in allowed_extensions:
                    error_message = (
                      f"File extension '{file_extension}' is not allowed. Allowed extensions are: {', '.join(allowed_extensions)}."
                    )
                    unique_errors.add(error_message)
            else:
                error_message = "Media duration is missing."
                unique_errors.add(error_message)

            # file_name = episode.file_name  # Assuming episode.file_name exists
            # if file_name:
            #     _, ext = os.path.splitext(file_name)
            #     ext = ext.lower().lstrip('.')
            #     allowed_extensions = media_checks[track_type]['allowed_extensions']
            #     if ext not in allowed_extensions:
            #         error_message = f"File extension '{ext}' is not allowed. Allowed extensions are: {', '.join(allowed_extensions)}."
            #         unique_errors.add(error_message)
            # else:
            #     error_message = "File name is missing."
            #     unique_errors.add(error_message)

        elif track_type == 'Video':
            # print(f"Checking {track_type} track")
            # Get height, bit_rate, frame_rate
            height = metadata.get('height', None)
            bit_rate = metadata.get('bit_rate', None)
            frame_rate = metadata.get('frame_rate', None)

            # Convert to appropriate numeric types
            try:
                height = float(height) if height is not None else None
            except ValueError:
                height = None
            try:
                bit_rate = float(bit_rate) if bit_rate is not None else None
            except ValueError:
                bit_rate = None
            try:
                frame_rate = float(frame_rate) if frame_rate is not None else None
            except ValueError:
                frame_rate = None

            # Initialize a flag to indicate if height matched any defined range
            height_matched = False

            # Check height to determine which bitrate range to use
            if height is not None:
                for height_check in media_checks[track_type]['height_checks']:
                    min_height, max_height = height_check['height_range']
                    if min_height <= height <= max_height:
                        height_matched = True
                        target_height = height_check['target_height']
                        min_bitrate, max_bitrate = height_check['bitrate_range']
                        # Now check bitrate
                        if bit_rate is not None:
                            if not (min_bitrate <= bit_rate <= max_bitrate):
                                warning_message = (
                                    f"Video track with height {target_height} pixels should have a bitrate between "
                                    f"{min_bitrate / 1_000_000}–{max_bitrate / 1_000_000} Mbps, but has "
                                    f"{bit_rate / 1_000_000:.2f} Mbps."
                                )
                                unique_warnings.add(warning_message)
                        else:
                            warning_message = "Video track bitrate is missing."
                            unique_warnings.add(warning_message)
                        break  # Exit the loop after finding a matching height range
                if not height_matched:
                    error_message = f"Video track has unexpected height {height} pixels."
                    unique_errors.add(error_message)
            else:
                error_message = "Video track height is missing."
                unique_errors.add(error_message)

            # Check frame_rate
            acceptable_frame_rates = media_checks[track_type]['acceptable_frame_rates']
            if frame_rate is not None:
                frame_rate_ok = any(abs(frame_rate - fr) < 0.1 for fr in acceptable_frame_rates)
                if not frame_rate_ok:
                    warning_message = (
                        f"Video track frame rate should be 29.97 or 23.98 fps, but is {frame_rate} fps."
                    )
                    unique_warnings.add(warning_message)
            else:
                warning_message = "Video track frame rate is missing."
                unique_warnings.add(warning_message)

        elif track_type == 'Audio':
            # print(f"Checking {track_type} track")
            # Get bit_rate, channels, sampling_rate
            bit_rate = metadata.get('bit_rate', None)
            channels = metadata.get('channel_s', None)
            sampling_rate = metadata.get('sampling_rate', None)

            # Convert to appropriate numeric types
            try:
                bit_rate = float(bit_rate) if bit_rate is not None else None
            except ValueError:
                bit_rate = None
            try:
                channels = int(channels) if channels is not None else None
            except ValueError:
                channels = None
            try:
                sampling_rate = int(sampling_rate) if sampling_rate is not None else None
            except ValueError:
                sampling_rate = None

            # Check bit_rate
            if bit_rate is not None:
                min_bitrate, max_bitrate = media_checks[track_type]['bitrate_range']
                if not (min_bitrate <= bit_rate <= max_bitrate):
                    warning_message = (
                        f"Audio track bitrate should be between "
                        f"{min_bitrate / 1000}–{max_bitrate / 1000} kbps, but is "
                        f"{bit_rate / 1000:.2f} kbps."
                    )
                    unique_warnings.add(warning_message)
            else:
                warning_message = "Audio track bitrate is missing."
                unique_warnings.add(warning_message)

            # Check channels
            if channels is not None:
                if channels not in media_checks[track_type]['channels']:
                    error_message = (
                        f"Audio track should have {media_checks[track_type]['channels']} channels, but has {channels} channels."
                    )
                    unique_errors.add(error_message)
            else:
                warning_message = "Audio track channel count is missing."
                unique_warnings.add(warning_message)

            # Check sampling_rate
            if sampling_rate is not None:
                if sampling_rate not in media_checks[track_type]['sampling_rates']:
                    error_message = (
                        f"Audio track sampling rate should be {media_checks[track_type]['sampling_rates'][0]} Hz, but is {sampling_rate} Hz."
                    )
                    unique_errors.add(error_message)
            else:
                warning_message = "Audio track sampling rate is missing."
                unique_warnings.add(warning_message)

    return unique_errors, unique_warnings


def create_presigned_view_url(bucket_name, object_name, expiration=3600):
    """Generate a pre-signed URL to view/download a file from S3."""
    # Load environment variables
    aws_access_key_id = env('AWS_ACCESS_KEY_ID', default=None)
    aws_secret_access_key = env('AWS_SECRET_ACCESS_KEY', default=None)
    aws_region = env('AWS_REGION', default='us-east-1')  # Optional default region

    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_name,
            },
            ExpiresIn=expiration
        )
        return response
    except (NoCredentialsError, PartialCredentialsError) as e:
        logging.error(f"Credentials error: {e}")
    except Exception as e:
        logging.error(f"Error generating pre-signed URL: {e}")
    return None
