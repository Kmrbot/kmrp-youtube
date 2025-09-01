import copy
import re
from dataclasses import dataclass

from database.db_manager import DBManager
from database.interface.db_impl_interface import DBCacheImplInterface
from nonebot.log import logger

from utils.loop_manager import LoopManager


@dataclass
class Key:
    channel_id: str
    msg_type: str
    msg_type_id: int


# 群组
class DBPluginsChannelData(DBCacheImplInterface):
    """
    key: {msg_type}_{msg_type_id}_{channel_id}
    """
    _default_value = {
        "video_on": True,  # 新视频
    }

    @classmethod
    def is_exist(cls, msg_type, msg_type_id, channel_id):
        """ 判断数据是否存在 """
        key = cls.generate_key(msg_type, msg_type_id, channel_id)
        data = cls.get_data_by_key(key)
        return data is not None

    @classmethod
    def add_default_data(cls, msg_type, msg_type_id, channel_id):
        """ 添加默认数据 """
        key = cls.generate_key(msg_type, msg_type_id, channel_id)
        data = cls.get_data_by_key(key)
        if data is not None:
            logger.error("add_default_data data already exist !")
            return
        cls.set_data_by_key(key, copy.deepcopy(cls._default_value))
        cls.__add_to_push_list(msg_type, msg_type_id, channel_id, "video")

    @classmethod
    def del_channel_data(cls, msg_type, msg_type_id, channel_id):
        """ 删除数据 """
        key = cls.generate_key(msg_type, msg_type_id, channel_id)
        cls.del_data(key)
        cls.__del_from_push_list(msg_type, msg_type_id, channel_id, "video")

    @classmethod
    def del_channel_data_by_msg_type_id(cls, msg_type, msg_type_id):
        """ 根据msgType和msgTypeID删除数据 """
        del_channel_ids = set()
        for k, data in copy.deepcopy(cls.get_data()).items():
            key_info = cls.analysis_key(k)
            if key_info.msg_type == msg_type and key_info.msg_type_id == msg_type_id:
                channel_id = key_info.channel_id
                del_channel_ids.add(channel_id)
                cls.del_channel_data(channel_id, msg_type, msg_type_id)
        return list(del_channel_ids)

    @classmethod
    def set_video_notify(cls, msg_type, msg_type_id, channel_id, is_notify):
        """ 设置视频推送状态 """
        key = cls.generate_key(msg_type, msg_type_id, channel_id)
        data = cls.get_data_by_key(key)
        if data is None:
            data = copy.deepcopy(cls._default_value)
        data["video_on"] = is_notify
        cls.set_data_by_key(key, data)

    @classmethod
    def get_video_notify(cls, msg_type, msg_type_id, channel_id):
        """ 获取视频推送状态 """
        key = cls.generate_key(msg_type, msg_type_id, channel_id)
        data = cls.get_data_by_key(key)
        return data["video_on"] if data is not None else False

    @classmethod
    def get_video_push_list(cls, channel_id):
        """ 获取channel_id对应推送视频的列表 """
        return LoopManager.get_list(f"youtube_channel_{channel_id}")

    @classmethod
    def get_follow_channels(cls, msg_type, msg_type_id):
        """ 获取正在关注着的频道ID """
        channels = []
        for k, data in cls.get_data().items():
            key_info = cls.analysis_key(k)
            if msg_type == key_info.msg_type and msg_type_id == key_info.msg_type_id:
                channels.append((key_info.channel_id, copy.deepcopy(data)))
        return channels

    @classmethod
    def get_video_push_channel_id(cls) -> str | None:
        """ 获取一个可能需要推送动态的UID """
        return LoopManager.next("youtube_channel_video")

    @classmethod
    def __add_to_push_list(cls, msg_type, msg_type_id, channel_id, style: str):
        """ 添加至推送列表里"""
        LoopManager.add(f"youtube_channel_{style}", channel_id)
        LoopManager.add(f"youtube_channel_{style}_{channel_id}", (msg_type, msg_type_id))

    @classmethod
    def __del_from_push_list(cls, msg_type, msg_type_id, channel_id, style: str):
        """ 从推送列表中删除 """
        LoopManager.delete(f"youtube_channel_{style}", channel_id)
        LoopManager.delete(f"youtube_channel_{style}_{channel_id}", (msg_type, msg_type_id))


    @classmethod
    def __analysis_channel_video_push_list(cls):
        for k, data in cls.get_data().items():
            key_info = cls.analysis_key(k)
            channel_id = key_info.channel_id
            if data["video_on"]:
                cls.__add_to_push_list(key_info.msg_type, key_info.msg_type_id, channel_id, "video")

    @classmethod
    def db_key_name(cls, bot_id):
        return f"{cls.__name__}_BOT_{bot_id}"

    @classmethod
    async def init(cls):
        """ 初始化 """
        cls.__analysis_channel_video_push_list()

    @classmethod
    def generate_key(cls, msg_type, msg_type_id, channel_id):
        """ 生成__data内存放的key """
        return f"{msg_type}_{msg_type_id}_{channel_id}"

    @classmethod
    def analysis_key(cls, key) -> Key:
        """ 解析generate_key生成的key """
        regex_groups = re.match("([a-zA-Z]*)_([0-9]*)_([a-zA-Z0-9_]*)", key).groups()
        return Key(
            msg_type=regex_groups[0],
            msg_type_id=int(regex_groups[1]),
            channel_id=regex_groups[2],
        )




DBManager.add_db(DBPluginsChannelData)
