from youtube_transcript_api import YouTubeTranscriptApi


def get_transcript(video_id):

    try:

        transcript = YouTubeTranscriptApi.get_transcript(
            video_id
        )

        text = ""

        for line in transcript:

            text += line["text"] + " "

        return text

    except Exception:

        return ""