from typing import Union, Tuple, Any
from nonebot.params import RegexGroup
from nonebot.rule import to_me
from .database.channel_data import DBPluginsChannelData
from protocol_adapter.protocol_adapter import ProtocolAdapter
from protocol_adapter.adapter_type import AdapterGroupMessageEvent, AdapterPrivateMessageEvent
from nonebot import on_regex
from utils.permission import white_list_handle
from .api.api import get_channel_info

del_channel = on_regex("^删除(Youtube|油管)频道 *([a-zA-Z0-9_]+)$",
                       rule=to_me(),
                       priority=5)
del_channel.__doc__ = """youtube"""
del_channel.__help_type__ = None

del_channel.handle()(white_list_handle("youtube"))


@del_channel.handle()
async def _(
        event: Union[AdapterGroupMessageEvent, AdapterPrivateMessageEvent],
        params: Tuple[Any, ...] = RegexGroup()
):
    channel_id = params[1]
    msg_type = ProtocolAdapter.get_msg_type(event)
    msg_type_id = ProtocolAdapter.get_msg_type_id(event)

    if not DBPluginsChannelData.is_exist(msg_type, msg_type_id, channel_id):
        return await del_channel.finish(ProtocolAdapter.MS.text("该频道尚未关注！"))
    DBPluginsChannelData.del_channel_data(msg_type, msg_type_id, channel_id)
    # 获取一下频道名
    channel_info = await get_channel_info(channel_id)
    return await del_channel.finish(
        ProtocolAdapter.MS.text(
            f"已删除Youtube频道 {channel_info['title'] if channel_info is not None else None}（{channel_id}）"
        )
    )
