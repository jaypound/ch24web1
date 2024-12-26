import uuid
import random
import datetime

def generate_sql_insert_statements(num_statements=4):
    # Static program_fk
    PROGRAM_FK = 'e0e05a06-88b5-4e1c-a3a4-a62fb4577fe2'

    # Possible choices
    AGE_RATING_CHOICES = [
        ('TV-Y', 'TV-Y: All Children'),
        ('TV-Y7', 'TV-Y7: Directed to Older Children'),
        ('TV-G', 'TV-G: General Audience'),
        ('TV-PG', 'TV-PG: Parental Guidance Suggested'),
        ('TV-14', 'TV-14: Parents Strongly Cautioned'),
        ('TV-MA', 'TV-MA: Mature Audience Only'),
    ]

    GENRE_CHOICES = [
        ('News/Weather Report', 'News/Weather Report'),
        ('News Magazine', 'News Magazine'),
        ('Documentary', 'Documentary'),
        ('Discussion/Interview/Debate', 'Discussion/Interview/Debate'),
        ('Talk Show', 'Talk Show'),
        ('Performing Arts', 'Performing Arts'),
        ('Fine Arts', 'Fine Arts'),
        ('Religion', 'Religion'),
        ('Popular Culture/Traditional Arts', 'Popular Culture/Traditional Arts'),
        ('Rock/Pop', 'Rock/Pop'),
        ('Folk/Traditional Music', 'Folk/Traditional Music'),
        ('Sports Magazine', 'Sports Magazine'),
        ('Team Sports', 'Team Sports'),
        ('Entertainment Programmes for 6-14', 'Entertainment Programmes for 6-14'),
        ('Informational/Educational/School Programmes', 'Informational/Educational/School Programmes'),
        ('Nature/Animals/Environment', 'Nature/Animals/Environment'),
        ('Technology/Natural Sciences', 'Technology/Natural Sciences'),
        ('Medicine/Physiology/Psychology', 'Medicine/Physiology/Psychology'),
        ('Magazines/Reports/Documentary', 'Magazines/Reports/Documentary'),
        ('Economics/Social Advisory', 'Economics/Social Advisory'),
        ('Tourism/Travel', 'Tourism/Travel'),
        ('Handicraft', 'Handicraft'),
        ('Fitness and Health', 'Fitness and Health'),
        ('Cooking', 'Cooking'),
    ]

    TIME_SLOT_CHOICES = [
        ('overnight', 'Overnight (2 AM - 6 AM)'),
        ('early_morning', 'Early Morning (6 AM - 9 AM)'),
        ('daytime', 'Daytime (9 AM - 3 PM)'),
        ('after_school', 'After School (3 PM - 6 PM)'),
        ('early_evening', 'Early Evening (6 PM - 8 PM)'),
        ('prime_time', 'Prime Time (8 PM - 11 PM)'),
        ('late_night', 'Late Night (11 PM - 2 AM)'),
    ]

    insert_statements = []

    # Generate the required number of INSERT statements
    for i in range(1, num_statements + 1):
        custom_id = str(uuid.uuid4())  # Random UUID
        # Pick random values
        age_rating = random.choice(AGE_RATING_CHOICES)[0]
        genre = random.choice(GENRE_CHOICES)[0]
        time_slot = random.choice(TIME_SLOT_CHOICES)[0]

        # We'll vary episode_number and file_name just to differentiate them
        episode_number = i
        episode_title = f"Episode {i} Title"
        file_name = f"episode{i:03}.mp4"
        transcription = f"Transcript of Episode {i}..."

        # Construct the single INSERT statement
        statement = f"""
INSERT INTO ch24app_episode (
    custom_id,
    episode_number,
    title,
    description,
    start_date,
    end_date,
    created_at,
    updated_at,
    program_id,
    created_by_id,
    file_name,
    has_mediainfo_errors,
    last_scheduled,
    last_timeslot,
    schedule_count,
    ai_age_rating,
    ai_genre,
    ai_summary,
    ai_time_slots_recommended,
    ai_topics,
    audience_engagement_reasons,
    audience_engagement_score,
    prohibited_content,
    prohibited_content_reasons,
    ready_for_air,
    transcription,
    duration_seconds,
    duration_timecode
) VALUES
(
    '{custom_id}',
    {episode_number},
    '{episode_title}',
    'description',
    '2024-01-01',
    '2024-01-01',
    NOW(),
    NOW(),
    '{PROGRAM_FK}',
    2,
    '{file_name}',
    false,
    NULL,
    NULL,
    0,
    '{age_rating}',
    '{genre}',
    'AI summary...',
    '{time_slot}',
    '{{"topic1","topic2"}}',
    'Engagement reasons...',
    85,
    NULL,
    NULL,
    true,
    '{transcription}',
    7560,
    '02:06:00'
);
"""
        insert_statements.append(statement.strip())

    return insert_statements

if __name__ == "__main__":
    statements = generate_sql_insert_statements(4)
    # Print each INSERT statement
    for stmt in statements:
        print(stmt)
        print()  # Blank line for readability

