# Import statements
from googleapiclient.discovery import build
import csv
import time

# Initialize the YouTube API client
API_KEY = "AIzaSyDdhPvCJS-U8zeDWGMwzQWq9L4aljZz_7k"
youtube = build("youtube", "v3", developerKey = API_KEY)

# List of search topics
search_queries = ["Children Education", "Education Technology"]
max_results_total = 100  # Limit to 100 videos per topic
videos_data = []         # Final list of all videos
seen_video_ids = set()   # Keep track of already seen videos to avoid duplicates

# Loop through each search topic
for query in search_queries:
    next_page_token = None
    fetched_results = 0
    query_videos_data = []  # Store results for the current topic

    # Keep fetching until we reach 100 videos
    while fetched_results < max_results_total:
        # Make a search request to the YouTube API
        request = youtube.search().list(
            q = query,
            part = "snippet",
            maxResults = 50,
            type = "video",
            pageToken = next_page_token
        )
        response = request.execute()

        video_ids = []
        # Extract video IDs, skipping duplicates
        for item in response['items']:
            video_id = item['id']['videoId']
            if video_id not in seen_video_ids:
                seen_video_ids.add(video_id)
                video_ids.append(video_id)

        # Trim if we are about to exceed 100 videos
        remaining = max_results_total - fetched_results
        video_ids = video_ids[:remaining]

        if not video_ids:
            break  # No new videos to add

        # Get detailed info about each video (title, views, etc.)
        video_details_request = youtube.videos().list(
            part = "snippet, statistics",
            id = ",".join(video_ids)
        )
        video_details = video_details_request.execute()

        # Extract relevant fields from each video
        for item in video_details['items']:
            title = item['snippet']['title']
            channel = item['snippet']['channelTitle']
            description = item['snippet']['description']
            views = item.get('statistics', {}).get('viewCount', '0')
            url = f"https://www.youtube.com/watch?v={item['id']}"

            # Save video info to the topic list
            query_videos_data.append([title, channel, description, views, url])

        fetched_results += len(video_ids)  # Keep count of how many we have added

        # Prepare for the next page of results, if available
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break  

        time.sleep(1)  # Avoid hitting rate limits

    # Add this topic's results to the final list
    videos_data.extend(query_videos_data)

# Save all collected data into a CSV file
with open('youtube_education_videos.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Title', 'Channel', 'Description', 'Views', 'URL'])  # Header row
    writer.writerows(videos_data)

    print(f"\n Done! {len(videos_data)} videos saved to 'youtube_education_videos.csv.")
