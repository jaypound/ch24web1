import boto3
import environ
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import logging
from .models import Episode, ScheduledEpisode
import time
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import models
from django.db.models import Min

# Load environment variables
env = environ.Env()
environ.Env.read_env()  # This loads variables from your .env file

logger = logging.getLogger(__name__)

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


def convert_seconds_to_timecode(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


from typing import Dict, Tuple, List
from enum import Enum

class ContentType(Enum):
    BUMPER = "bumper"
    SHORTFORM = "shortform"
    LONGFORM = "longform"

SHORTFORM_BLOCK_MAX_DURATION = 120

# Define time slots with their specific times and content ratings
TIME_SLOTS = {
    'early_morning': {
        'start': '05:00:00',
        'end': '09:00:00',
        'seconds': 14400,
        'ratings': ['TV-Y', 'TV-Y7', 'TV-G']
    },
    'daytime': {
        'start': '09:00:00',
        'end': '15:00:00',  # 3 PM
        'seconds': 21600,
        'ratings': ['TV-Y', 'TV-Y7', 'TV-G']
    },
    'after_school': {
        'start': '15:00:00',  # 3 PM
        'end': '18:00:00',  # 6 PM
        'seconds': 10800,
        'ratings': ['TV-Y7', 'TV-G', 'TV-PG']
    },
    'early_evening': {
        'start': '18:00:00',  # 6 PM
        'end': '20:00:00',  # 8 PM
        'seconds': 7200,
        'ratings': ['TV-G', 'TV-PG']
    },
    'prime_time': {
        'start': '20:00:00',  # 8 PM
        'end': '23:00:00',  # 11 PM
        'seconds': 10800,
        'ratings': ['TV-PG', 'TV-14']
    },
    'late_night': {
        'start': '23:00:00',  # 11 PM
        'end': '02:00:00',  # 2 AM
        'seconds': 10800,
        'ratings': ['TV-14', 'TV-MA']
    },
    'overnight': {
        'start': '02:00:00',  # 2 AM
        'end': '05:00:00',  # 6 AM
        'seconds': 10800,
        'ratings': ['TV-MA']
    }
}

def get_content_type(duration_seconds: int) -> ContentType:
    """Determine content type based on duration"""
    if duration_seconds <= 15:
        return ContentType.BUMPER
    elif duration_seconds <= 900:  # 15 minutes
        return ContentType.SHORTFORM
    else:
        return ContentType.LONGFORM
    

def schedule_episode(episode: Episode, schedule_date, current_dt, slot_name: str):
    """Schedule a single episode with logging"""

    # start_dt is the same as current_dt (already a datetime)
    start_dt = current_dt  
    end_dt = start_dt + timedelta(seconds=episode.duration_seconds)

    # (Optionally make it timezone-aware if needed)
    # start_dt = timezone.make_aware(start_dt)
    # end_dt = timezone.make_aware(end_dt)

    logger.info(f"Scheduling episode: {episode.title}")
    logger.info(f"Start time: {start_dt}")
    logger.info(f"End time: {end_dt}")
    logger.info(f"Duration: {episode.duration_seconds}s")
    logger.info(f"Rating: {episode.ai_age_rating}")

    try:
        # Create scheduled episode record first
        scheduled = ScheduledEpisode.objects.create(
            episode=episode,
            program=episode.program,
            creator=episode.program.creator,
            schedule_date=schedule_date,
            start_time=start_dt,
            end_time=end_dt,
            episode_number=episode.episode_number,
            title=episode.title,
            file_name=episode.file_name,
            ai_genre=episode.ai_genre,
            ai_age_rating=episode.ai_age_rating,
            ai_topics=episode.ai_topics,
            ai_time_slots_recommended=episode.ai_time_slots_recommended,
            audience_engagement_score=episode.audience_engagement_score,
            audience_engagement_reasons=episode.audience_engagement_reasons,
            prohibited_content=episode.prohibited_content,
            prohibited_content_reasons=episode.prohibited_content_reasons,
            ready_for_air=episode.ready_for_air,
            duration_seconds=episode.duration_seconds,
            duration_timecode=episode.duration_timecode,
        )
        logger.info("Successfully created ScheduledEpisode record")
        
        # Update episode scheduling info in a single operation
        Episode.objects.filter(custom_id=episode.custom_id).update(
            last_timeslot=slot_name,
            last_scheduled=timezone.now(),
            schedule_count=models.F('schedule_count') + 1,
            priority_score=models.F('priority_score') + 1
        )
        logger.info("Successfully updated episode scheduling metadata")
        
    except Exception as e:
        logger.error(f"Error scheduling episode: {str(e)}")
        raise
    
    return end_dt


def schedule_episodes(schedule_date, creator_id=None, all_ready=True):
    """Enhanced scheduling function with structured slot-based scheduling and limits"""
    
    logger.info(f"******************* Starting scheduling for date: {schedule_date} *******************")

    # Build base query
    if all_ready:
        base_query = Episode.objects.all()
    else:
        base_query = Episode.objects.filter(ready_for_air=True)
        
    if creator_id:
        base_query = base_query.filter(program__creator_id=creator_id)
    elif not all_ready:
        logger.warning("Neither creator_id nor all_ready specified. Exiting.")
        return

    # Validate available content
    available_content = base_query.count()
    logger.info(f"Found {available_content} available episodes")
    if not available_content:
        logger.warning("No content available for scheduling")
        return

    steps = 0
    MAX_STEPS = 100
    current_dt = None
    MAX_CONSECUTIVE_SHORTFORM = 4
    MIN_REMAINING_TIME = 300  # 5 minutes minimum

    # Process each time slot
    for slot_name, slot_info in TIME_SLOTS.items():
        logger.info(f"******** Processing slot: {slot_name} ********")

        slot_start_str = slot_info['start']
        slot_duration_sec = slot_info['seconds']
        
        # Convert the slot's start time to a datetime on schedule_date
        slot_start_time = datetime.strptime(slot_start_str, '%H:%M:%S').time()
        slot_start_dt = datetime.combine(schedule_date, slot_start_time)
        slot_end_dt = slot_start_dt + timedelta(seconds=slot_duration_sec)

        # Initialize current_dt for the first slot
        if current_dt is None:
            current_dt = slot_start_dt
        
        logger.info(f"Current datetime: {current_dt}")
        consecutive_shortform = 0

        if steps >= MAX_STEPS:
            logger.info(f"Max steps reached ({MAX_STEPS}). Exiting.")
            break

        # Handle overnight wraparound
        if slot_end_dt < current_dt:
            slot_start_dt += timedelta(days=1)
            slot_end_dt += timedelta(days=1)
            logger.info("Slot crosses midnight, adjusted dates")

        while (current_dt < slot_end_dt) and (steps < MAX_STEPS):
            steps += 1
            remaining_in_slot = (slot_end_dt - current_dt).total_seconds()
            
            if remaining_in_slot < MIN_REMAINING_TIME:
                logger.info(f"Not enough time left in slot ({remaining_in_slot}s). Moving to next slot.")
                current_dt = slot_end_dt  # Force move to next slot
                break

            # Try to schedule content in order: LONGFORM, SHORTFORM, BUMPER
            content_scheduled = False
            
            # Try LONGFORM
            longform = get_suitable_content(base_query, slot_name, ContentType.LONGFORM, remaining_in_slot)
            if longform and validate_episode(longform):
                try:
                    current_dt = schedule_episode(longform, schedule_date, current_dt, slot_name)
                    content_scheduled = True
                    consecutive_shortform = 0
                except Exception as e:
                    logger.error(f"Failed to schedule longform: {str(e)}")

            # Try SHORTFORM if no longform was scheduled
            if not content_scheduled and consecutive_shortform < MAX_CONSECUTIVE_SHORTFORM:
                shortform = get_suitable_content(base_query, slot_name, ContentType.SHORTFORM, remaining_in_slot)
                if shortform and validate_episode(shortform):
                    try:
                        current_dt = schedule_episode(shortform, schedule_date, current_dt, slot_name)
                        content_scheduled = True
                        consecutive_shortform += 1
                    except Exception as e:
                        logger.error(f"Failed to schedule shortform: {str(e)}")

            # Try BUMPER if nothing else was scheduled
            if not content_scheduled:
                bumper = get_suitable_content(base_query, slot_name, ContentType.BUMPER, remaining_in_slot)
                if bumper and validate_episode(bumper):
                    try:
                        current_dt = schedule_episode(bumper, schedule_date, current_dt, slot_name)
                        content_scheduled = True
                        consecutive_shortform = 0
                    except Exception as e:
                        logger.error(f"Failed to schedule bumper: {str(e)}")

            # If no content could be scheduled at all, move to the next slot
            if not content_scheduled:
                logger.info("No suitable content found for current slot. Moving to next slot.")
                current_dt = slot_end_dt  # Force move to next slot
                break

        logger.info(f"******** Done processing slot: {slot_name} ********")

    logger.info(f"******************* Ending scheduling for date: {schedule_date} *******************")


def validate_episode(episode):
    """Validate that an episode has all required fields"""
    required_fields = [
        'episode_number',
        'title',
        'ai_genre',
        'ai_age_rating',
        'duration_seconds',
        'duration_timecode'
    ]
    
    for field in required_fields:
        if not getattr(episode, field):
            logger.warning(f"Episode {episode.custom_id} missing required field: {field}")
            return False
    return True


def get_slot_for_time(current_time):
    """Determine which time slot a given time falls into"""
    for slot_name, slot_info in TIME_SLOTS.items():
        slot_start = datetime.strptime(slot_info['start'], '%H:%M:%S').time()
        slot_end = datetime.strptime(slot_info['end'], '%H:%M:%S').time()
        
        # Special handling for late_night slot that crosses midnight
        if slot_name == 'late_night':
            if current_time >= slot_start or current_time <= slot_end:
                return slot_name
        else:
            if slot_start <= current_time <= slot_end:
                return slot_name
                
    return 'overnight'  # Default to overnight if no match


def _remaining_seconds(current_time, end_time):
    """Calculate remaining seconds in the time slot"""
    if end_time > current_time:
        delta = datetime.combine(datetime.today(), end_time) - \
                datetime.combine(datetime.today(), current_time)
    else:
        # Handle overnight slots
        delta = datetime.combine(datetime.today() + timedelta(days=1), end_time) - \
                datetime.combine(datetime.today(), current_time)
    return delta.total_seconds()


def _add_time(time, delta):
    """Add timedelta to time, handling overnight wraparound"""
    datetime_combined = datetime.combine(datetime.today(), time)
    new_datetime = datetime_combined + delta
    return new_datetime.time()


def get_suitable_content(query, slot_name: str, content_type: ContentType, 
                        remaining_time: int) -> Episode:
    """Get appropriate content for the current slot and time"""
    ratings = TIME_SLOTS[slot_name]['ratings']
    
    duration_filter = {}
    if content_type == ContentType.BUMPER:
         max_duration = min(remaining_time, 15)
         duration_filter = {'duration_seconds__lte': max_duration}

    elif content_type == ContentType.SHORTFORM:
        # "somewhere between >15 and ≤900" 
        # BUT also must not exceed remaining_time
        # so unify the lte constraint into min(900, remaining_time)
        duration_filter = {
            'duration_seconds__gt': 15,
            'duration_seconds__lte': min(900, remaining_time),
        }
    else:  # LONGFORM
        duration_filter = {'duration_seconds__gt': 900}
        
    return query.filter(
        ai_age_rating__in=ratings,
        **duration_filter
    ).order_by(
        'priority_score',             # Prioritize less-scheduled content
        '-audience_engagement_score', # Then by engagement
        'schedule_count',             # Then by frequency
        'last_scheduled'              # Then by recency
    ).first()




