import json
from nonebot.log import logger
from utils import get_config_path


def get_youtube_config_data():
    try:
        # 每次都重新加载 即可以动态重载 性能消耗可忽略
        with open(get_config_path().joinpath("youtube/config.json"), "r", encoding="utf8") as file:
            data = json.load(file)
    except json.JSONDecodeError:
        logger.error("get_youtube_config_data json decode fail !")
        return None
    return data


def get_youtube_monitor_server_addr_port():
    data = get_youtube_config_data()
    if data is not None:
        return data["youtubeMonitorServerAddr"], data["youtubeMonitorServerPort"]
    else:
        return "", ""


def get_youtube_monitor_server_get_channel_info_entry():
    data = get_youtube_config_data()
    if data is not None:
        return data["getChannelInfoEntry"]
    else:
        return ""


def get_youtube_monitor_server_get_vide_list_entry():
    data = get_youtube_config_data()
    if data is not None:
        return data["getVideoListEntry"]
    else:
        return ""


def get_youtube_api_key() -> str:
    data = get_youtube_config_data()
    if data is not None:
        return data["apiKey"]
    else:
        return ""
