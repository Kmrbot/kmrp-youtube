import datetime

from nonebot import logger
from protocol_adapter.protocol_adapter import ProtocolAdapter
from utils.push_manager import PushManager
from ..database.channel_data import DBPluginsChannelData
from utils.publish_subscribe_manager import PublishSubscribeManager
from ..api.api import get_channel_info, get_video_list

all_channel_info = {}


async def youtube_channel_video_update(**kwargs):
    channel_id = DBPluginsChannelData.get_video_push_channel_id()
    if channel_id is None:
        return
    if all_channel_info.get(channel_id) is None:
        # 没数据先拉一遍
        channel_info = get_channel_info(channel_id)
        if channel_info is None:
            logger.error(f"youtube_channel_video_update cannot get_channel_info ! channel_id = {channel_id}")
            return
        all_channel_info[channel_id] = {
            "channel_info": channel_info,
            "videos": {
                "cur_newest_video": None,
                "need_update_videos": [],
            },
        }
    playlist_id = all_channel_info[channel_id]["channel_info"]["playlist_id"]
    video_list = get_video_list(channel_id, playlist_id)
    for video in video_list["videos"]:
        # 按时间来排就行
        if all_channel_info[channel_id]["videos"]["cur_newest_video"] is None:
            all_channel_info[channel_id]["videos"]["cur_newest_video"] = video
        elif video.publishTimestamp > all_channel_info[channel_id]["videos"]["cur_newest_video"].publishTimestamp:
            # 时间大于的全部统一推送
            all_channel_info[channel_id]["videos"]["need_update_videos"].append(video)


async def youtube_channel_video_push(**kwargs):
    # 其实可以保存一个当前遍历到的ID，但是也可以直接全部遍历一遍
    for channel_id, channel_info in all_channel_info.items():
        # 如果need_update_videos有内容说明需要推送了
        if len(channel_info["videos"]["need_update_videos"]) == 0:
            continue
        for video in channel_info["videos"]["need_update_videos"]:
            logger.info(f"Youtube video update ({video.title}) "
                        f"Channel {video.ownerChannelTitle}({video.ownerChannelID})")
            # 获取这个channel_id都要发到哪些地方
            push_list = DBPluginsChannelData.get_video_push_list(channel_id)
            for single_push_data in push_list:
                publish_time = datetime.datetime.fromtimestamp(video.publishTimestamp).strftime("%Y-%m-%d %H:%M:%S")
                PushManager.notify(PushManager.PushData(
                    msg_type=single_push_data[0],
                    msg_type_id=single_push_data[1],
                    message=ProtocolAdapter.MS.text("Youtube频道视频更新：\n\n"
                                                    f"频道：{video.ownerChannelTitle}\n"
                                                    f"频道ID：{video.ownerChannelID}\n"
                                                    f"视频标题：{video.title}\n"
                                                    f"发布时间：{publish_time}\n"
                                                    f"视频简介：{video.description}")
                ))
        # 更新最新的video，设置成第一个就行
        channel_info["videos"]["cur_newest_video"] = channel_info["videos"]["need_update_videos"][0]
        # 清空掉更新列表
        channel_info["videos"]["need_update_videos"] = []


PublishSubscribeManager.subscribe("youtube_channel_video_update", youtube_channel_video_update)
PublishSubscribeManager.subscribe("youtube_channel_video_push", youtube_channel_video_push)
