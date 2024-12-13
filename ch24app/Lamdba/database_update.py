import os
import json
import boto3
import psycopg2
import psycopg2.extras
import uuid

# Retrieve DB config from environment variables
DB_NAME = os.environ.get('DATABASE_NAME')
DB_USER = os.environ.get('DATABASE_USER')
DB_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DB_HOST = os.environ.get('DATABASE_HOST')
DB_PORT = os.environ.get('DATABASE_PORT')

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # Parse S3 event
    for record in event.get('Records', []):
        bucket_name = record['s3']['bucket']['name']
        file_key = record['s3']['object']['key']
        
        # file_key looks like: "0709bcd8-ea0c-4fab-989c-5b113053e16c/4minute_sample.json"
        # The folder name (first segment) = episode_custom_id
        parts = file_key.split('/')
        episode_custom_id = parts[0]  # The first part before the slash

        # Download and parse JSON
        json_data = download_json_from_s3(bucket_name, file_key)

        # Update database
        update_episode_record(episode_custom_id, json_data)

    return {"status": "success"}


def download_json_from_s3(bucket_name, file_key):
    response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    data = response['Body'].read().decode('utf-8')
    return json.loads(data)


def update_episode_record(episode_custom_id, json_data):
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True

    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        # Fetch the episode_id for the foreign key
        # Adjust table names as needed. This example assumes 'ch24app_episode' is correct.
        cur.execute("SELECT custom_id FROM ch24app_episode WHERE custom_id = %s", (episode_custom_id,))
        episode_row = cur.fetchone()
        if not episode_row:
            raise ValueError(f"No episode found with custom_id {episode_custom_id}")

        episode_id = episode_row['custom_id']

        # Extract fields from JSON
        transcription = json_data.get("transcription", "")
        ai_summary = json_data.get("ai_summary", "")
        ai_genre = json_data.get("ai_genre", "")
        ai_age_rating = json_data.get("ai_age_rating", "")
        ai_topics = json_data.get("ai_topics", [])
        ai_time_slots_recommended = json_data.get("ai_time_slots_recommended", "")
        audience_engagement_score = json_data.get("audience_engagement_score", None)
        audience_engagement_reasons = json_data.get("audience_engagement_reasons", "")
        use_analysis = json_data.get("use_analysis", True)
        prohibited_content = json_data.get("prohibited_content", [])
        prohibited_content_reasons = json_data.get("prohibited_content_reasons", "")

        # Generate a unique custom_id for this analysis record

        update_query = """
        UPDATE ch24app_episode (
            transcription,
            ai_summary,
            ai_genre,
            ai_age_rating,
            ai_topics,
            ai_time_slots_recommended,
            audience_engagement_score,
            audience_engagement_reasons,
            use_analysis,
            prohibited_content,
            prohibited_content_reasons,
            created_at,
            updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
        )
        """

        cur.execute(
            insert_query,
            (
                transcription,
                ai_summary,
                ai_genre,
                ai_age_rating,
                ai_topics,
                ai_time_slots_recommended,
                audience_engagement_score,
                audience_engagement_reasons,
                use_analysis,
                prohibited_content,
                prohibited_content_reasons
            )
        )

        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                # Fetch has_mediainfo_errors for the episode
            cur.execute(
                "SELECT has_mediainfo_errors FROM ch24app_episode WHERE custom_id = %s",
                (episode_custom_id,)
            )
            episode_row = cur.fetchone()
            if not episode_row:
                raise ValueError(f"No episode found with custom_id {episode_custom_id}")

            has_mediainfo_errors = episode_row['has_mediainfo_errors']

            # Determine if ready_for_air should be set to False
            if prohibited_content is not None or has_mediainfo_errors:
                update_query = """
                    UPDATE ch24app_episode
                    SET ready_for_air = FALSE,
                        updated_at = NOW()
                    WHERE custom_id = %s
                """
                cur.execute(update_query, (episode_custom_id,))
                print(f"Updated ready_for_air to FALSE for episode_custom_id: {episode_custom_id}")
            else:
                print(f"No update required for episode_custom_id: {episode_custom_id}")

    except psycopg2.Error as e:
        raise Exception(f"Database operation failed: {e}")
    finally:
        conn.close()
    conn.close()