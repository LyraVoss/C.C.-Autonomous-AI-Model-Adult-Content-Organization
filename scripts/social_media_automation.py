try:
    import tweepy
except ImportError:
    tweepy = None

from instabot import Bot
import time
from typing import Dict, List
import os
from decouple import config

class SocialMediaManager:
    def __init__(self):
        self.twitter_api = self._setup_twitter()
        self.instagram_bot = self._setup_instagram()

    def _setup_twitter(self):
        auth = tweepy.OAuth1UserHandler(
            config('TWITTER_API_KEY'),
            config('TWITTER_API_SECRET'),
            config('TWITTER_ACCESS_TOKEN'),
            config('TWITTER_ACCESS_TOKEN_SECRET')
        )
        return tweepy.API(auth)

    def _setup_instagram(self):
        bot = Bot()
        bot.login(username=config('INSTAGRAM_USERNAME'), password=config('INSTAGRAM_PASSWORD'))
        return bot

    def post_to_twitter(self, content: str, image_path: str = None):
        try:
            if image_path:
                media = self.twitter_api.media_upload(image_path)
                self.twitter_api.update_status(status=content, media_ids=[media.media_id])
            else:
                self.twitter_api.update_status(status=content)
            print("Posted to Twitter successfully")
        except Exception as e:
            print(f"Error posting to Twitter: {e}")

    def post_to_instagram(self, content: str, image_path: str):
        try:
            self.instagram_bot.upload_photo(image_path, caption=content)
            print("Posted to Instagram successfully")
        except Exception as e:
            print(f"Error posting to Instagram: {e}")

    def schedule_posts(self, posts: List[Dict]):
        for post in posts:
            platform = post['platform']
            content = post['content']
            image = post.get('image')
            delay = post.get('delay', 0)

            time.sleep(delay)

            if platform == 'twitter':
                self.post_to_twitter(content, image)
            elif platform == 'instagram':
                if image:
                    self.post_to_instagram(content, image)
                else:
                    print("Instagram requires an image")

if __name__ == "__main__":
    # Example usage
    manager = SocialMediaManager()
    manager.post_to_twitter("Hello from C.C. AI Model!")