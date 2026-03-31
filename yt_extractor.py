import yt_dlp

def get_video_metadata(url):
    """
    Extracts the Title, Channel, and Duration from a YouTube URL.
    This is the engine that fills your database automatically!
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # We fetch the info without downloading the actual video
            info = ydl.extract_info(url, download=False)
            
            return {
                "video_id": info.get("id"),
                "title": info.get("title"),
                "channel": info.get("uploader"),
                "duration_seconds": info.get("duration"),
                "url": url
            }
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return None

# --- TEST BLOCK ---
if __name__ == "__main__":
    test_url = "https://www.youtube.com/watch?v=KMkmA4i2FQc"
    print("Extracting info...")
    data = get_video_metadata(test_url)
    
    if data:
        print(f"Success! Found: {data['title']} by {data['channel']}")
        print(f"Duration: {data['duration_seconds']} seconds")