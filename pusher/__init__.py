from nonebot_plugin_apscheduler import scheduler
from utils.plugin_registry import is_plugin_active
from utils.publish_subscribe_manager import PublishSubscribeManager
from .pusher import *  # noqa: F401


@scheduler.scheduled_job("interval", seconds=10, id="pusher")
async def dynamic_live_sche_callback():
    if not is_plugin_active("youtube"):
        return
    PublishSubscribeManager.publish("youtube_channel_video_update")
    PublishSubscribeManager.publish("youtube_channel_video_push")
