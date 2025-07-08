from typing import Union, Tuple, Any
from nonebot.internal.matcher import Matcher
from nonebot.params import RegexGroup
from nonebot.rule import to_me
from .database.channel_data import DBPluginsChannelData
from protocol_adapter.protocol_adapter import ProtocolAdapter
from protocol_adapter.adapter_type import AdapterGroupMessageEvent, AdapterPrivateMessageEvent, AdapterMessage
from nonebot import on_regex
from utils.permission import white_list_handle
from .api.api import get_channel_info


follow_channel = on_regex("^添加(Youtube|油管)频道 *([a-zA-Z0-9_]+)$",
                          rule=to_me(),
                          priority=5)
follow_channel.__doc__ = """youtube"""
follow_channel.__help_type__ = None

follow_channel.handle()(white_list_handle("youtube"))


@follow_channel.handle()
async def _(
        matcher: Matcher,
        event: Union[AdapterGroupMessageEvent, AdapterPrivateMessageEvent],
        params: Tuple[Any, ...] = RegexGroup()
):
    channel_id = params[1]
    msg_type = ProtocolAdapter.get_msg_type(event)
    msg_type_id = ProtocolAdapter.get_msg_type_id(event)
    # 获取一下频道名
    channel_info = get_channel_info(channel_id)
    if channel_info is None:
        await follow_channel.finish("获取频道信息失败！")
    if DBPluginsChannelData.is_exist(msg_type, msg_type_id, channel_id):
        await follow_channel.finish("该频道已关注！")
    DBPluginsChannelData.add_default_data(msg_type, msg_type_id, channel_id)
    await follow_channel.finish(f"已关注频道 {channel_info['title']}（{channel_id}）")
