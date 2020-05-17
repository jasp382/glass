"""
Get data From Youtube
"""

def save_video(video_url, outfolder):

    from pytube import YouTube

    video = YouTube(video_url)

    video.streams.get_by_itag(18).download(outfolder)

