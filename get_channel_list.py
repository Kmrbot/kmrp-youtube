from typing import Union
from nonebot.rule import to_me
from .database.channel_data import DBPluginsChannelData
from protocol_adapter.protocol_adapter import ProtocolAdapter
from protocol_adapter.adapter_type import AdapterGroupMessageEvent, AdapterPrivateMessageEvent
from nonebot import on_regex
from utils.permission import white_list_handle


get_channel_list = on_regex("^(Youtube|油管)频道列表",
                            rule=to_me(),
                            priority=5)
get_channel_list.__doc__ = """youtube"""
get_channel_list.__help_type__ = None

get_channel_list.handle()(white_list_handle("youtube"))


@get_channel_list.handle()
async def _(
        event: Union[AdapterGroupMessageEvent, AdapterPrivateMessageEvent],
):
    msg_type = ProtocolAdapter.get_msg_type(event)
    msg_type_id = ProtocolAdapter.get_msg_type_id(event)
    channels = DBPluginsChannelData.get_follow_channels(msg_type, msg_type_id)
    ret_str = "当前已关注Youtube频道列表：\n\n"
    for channel in channels:
        ret_str += f"频道ID：{channel[0]} 通知：{'开' if channel[1]['video_on'] else '关'}\n"
    return await get_channel_list.finish(ProtocolAdapter.MS.text(ret_str))
