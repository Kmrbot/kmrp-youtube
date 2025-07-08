import copy
import re

from database.db_manager import DBManager
from database.interface.db_impl_interface import DBCacheImplInterface
from nonebot.log import logger


# 群组
class DBPluginsChannelData(DBCacheImplInterface):
    """
    key: {msg_type}_{msg_type_id}_{channel_id}
    """
    _default_value = {
        "video_on": True,  # 新视频
    }
    __push_dict = {}
    __push_index = {}

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
    def del_user_data(cls, msg_type, msg_type_id, channel_id):
        """ 删除数据 """
        key = cls.generate_key(msg_type, msg_type_id, channel_id)
        cls.del_data(key)
        cls.__del_from_push_list(msg_type, msg_type_id, channel_id, "video")

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
        return cls.__push_dict["video"].get(channel_id, [])

    @classmethod
    def get_follow_channels(cls, msg_type, msg_type_id):
        """ 获取正在关注着的频道ID """
        channels = []
        for k, data in cls.get_data().items():
            key_info = cls.analysis_key(k)
            if msg_type == key_info["msg_type"] and msg_type_id == key_info["msg_type_id"]:
                channels.append((key_info["channel_id"], copy.deepcopy(data)))
        return channels

    @classmethod
    def get_video_push_channel_id(cls) -> str | None:
        """ 获取一个可能需要推送动态的UID """
        if len(cls.__push_dict.get("video", [])) == 0:
            return None
        index = cls.__push_index.get("video", 0)
        if index >= len(cls.__push_dict["video"]):
            index = 0
        cls.__push_index["video"] = 0 if index + 1 >= len(cls.__push_dict["video"]) else index + 1
        # 字典扩容重牌也无所谓 无非是顺序错了一次
        return list(cls.__push_dict["video"].keys())[index]

    @classmethod
    def __add_to_push_list(cls, msg_type, msg_type_id, channel_id, style: str):
        """ 添加至推送列表里"""
        if cls.__push_dict.get(style) is None:
            cls.__push_dict[style] = {}
        if cls.__push_dict[style].get(channel_id) is None:
            cls.__push_dict[style][channel_id] = []
        if (msg_type, msg_type_id) not in cls.__push_dict[style][channel_id]:
            cls.__push_dict[style][channel_id].append((msg_type, msg_type_id))

    @classmethod
    def __del_from_push_list(cls, msg_type, msg_type_id, channel_id, style: str):
        """ 从推送列表中删除 """
        if cls.__push_dict.get(style) is None:
            logger.error(f"__del_from_push_list not invalid style ! style = {style}")
            return
        if cls.__push_dict[style].get(channel_id) is None:
            return
        if (msg_type, msg_type_id) in cls.__push_dict[style][channel_id]:
            cls.__push_dict[style][channel_id].remove((msg_type, msg_type_id))
        if len(cls.__push_dict[style][channel_id]) == 0:
            cls.__push_dict[style].pop(channel_id)

    @classmethod
    def __analysis_channel_video_push_list(cls):
        cls.__push_dict = {}
        for k, data in cls.get_data().items():
            key_info = cls.analysis_key(k)
            channel_id = key_info["channel_id"]
            if data["video_on"]:
                cls.__add_to_push_list(key_info["msg_type"], key_info["msg_type_id"], channel_id, "video")

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
    def analysis_key(cls, key):
        """ 解析generate_key生成的key """
        regex_groups = re.match("([a-zA-Z]*)_([0-9]*)_([a-zA-Z0-9_]*)", key).groups()
        if regex_groups is not None:
            return {
                "msg_type": regex_groups[0],
                "msg_type_id": int(regex_groups[1]),
                "channel_id": regex_groups[2]
            }


DBManager.add_db(DBPluginsChannelData)
