from nonebot_plugin_apscheduler import scheduler
from .pusher import *


@scheduler.scheduled_job("interval", seconds=10, id="pusher")
async def dynamic_live_sche_callback():
    PublishSubscribeManager.publish("youtube_channel_video_update")
    PublishSubscribeManager.publish("youtube_channel_video_push")
