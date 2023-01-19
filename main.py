import argparse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Set the API key
API_KEY = 'YOUR_API_KEY'

def upload_video(youtube, video_metadata, video_file_path):
    """Upload a video to YouTube"""
    # Create the media file upload object
    media = MediaFileUpload(video_file_path, resumable=True)

    # Insert the video
    request = youtube.videos().insert(
        part=','.join(video_metadata.keys()),
        body=video_metadata,
        media_body=media
    )
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f'{int(status.progress() * 100)}% uploaded')
    print(f'Video ID: {response["id"]} was uploaded successfully')

def get_comments(youtube, video_id):
    """Get all comments on a YouTube video"""
    comments = []
    request = youtube.commentThreads().list(comments = [])
    request = youtube.commentThreads().list(
        part='snippet',
        videoId=video_id,
        textFormat='plainText'
    )
    while request:
        response = request.execute()
        comments += response['items']
        request = youtube.commentThreads().list_next(request, response)
    return comments

def delete_comment(youtube, comment_id):
    """Delete a comment on a YouTube video"""
    youtube.comments().delete(id=comment_id).execute()
    print(f'Comment with ID {comment_id} has been deleted.')

def create_parser():
    """Create argparse parser"""
    parser = argparse.ArgumentParser(description='YouTube video uploader and comment manager')
    parser.add_argument('--upload', metavar='video_file', type=str, help='Upload a video to YouTube')
    parser.add_argument('--title', metavar='title', type=str, help='The title of the video')
    parser.add_argument('--description', metavar='description', type=str, help='The description of the video')
    parser.add_argument('--tags', metavar='tags', type=str, nargs='+', help='The tags of the video')
    parser.add_argument('--category', metavar='category_id', type=str, help='The category of the video')
    parser.add_argument('--privacy', metavar='privacy_status', type=str, help='The privacy status of the video')
    parser.add_argument('--comments', metavar='video_id', type=str, help='Manage comments on a YouTube video')
    parser.add_argument('--keywords', metavar='keywords', type=str, nargs='+', help='Keywords to search for in comments')
    parser.add_argument('--delete', action='store_true', help='Delete comments containing the keywords')
    return parser

if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    if args.upload:
        video_metadata = {
            'snippet': {
                'title': args.title,
                'description': args.description,
                'tags': args.tags,
                'categoryId': args.category
            },
            'status': {
                'privacyStatus': args.privacy,
            }
        }
    try:
        upload_video(youtube, video_metadata, args.upload)
    except HttpError as error:
        print(f'An error occurred: {error}')
elif args.comments:
    if args.keywords and args.delete:
        try:
            comments = get_comments(youtube, args.comments)
            for comment in comments:
                comment_text = comment['snippet']['topLevelComment']['snippet']['textDisplay']
                comment_id = comment['snippet']['topLevelComment']['id']
                if all(keyword in comment_text for keyword in args.keywords):
                    delete_comment(youtube, comment_id)
            print('Comments containing the keywords have been deleted.')
        except HttpError as error:
            print(f'An error occurred: {error}')
    else:
        print("Please provide keywords and use the --delete flag to delete them.")
else:
    print("Please provide either --upload or --comments flag to use the script.")
