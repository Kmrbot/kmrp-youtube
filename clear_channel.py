from typing import Union
from nonebot.rule import to_me
from .database.channel_data import DBPluginsChannelData
from protocol_adapter.protocol_adapter import ProtocolAdapter
from protocol_adapter.adapter_type import AdapterGroupMessageEvent, AdapterPrivateMessageEvent, AdapterMessage
from nonebot import on_regex
from utils.permission import white_list_handle
from .api.api import get_channel_info


clear_channel = on_regex("^清空(Youtube|油管)频道",
                         rule=to_me(),
                         priority=5)
clear_channel.__doc__ = """youtube"""
clear_channel.__help_type__ = None

clear_channel.handle()(white_list_handle("youtube"))

@clear_channel.handle()
async def _(
        event: Union[AdapterGroupMessageEvent, AdapterPrivateMessageEvent],
):
    msg_type = ProtocolAdapter.get_msg_type(event)
    msg_type_id = ProtocolAdapter.get_msg_type_id(event)

    del_list = DBPluginsChannelData.del_channel_data_by_msg_type_id(msg_type, msg_type_id)
    if len(del_list) == 0:
        ret_str = "当前无任何关注，跳过操作。"
    else:
        ret_str = "已成功删除Youtube频道：\n"
        for del_channel_id in del_list:
            ret_str += f"Youtube频道ID：{del_channel_id}\n"
    return await clear_channel.finish(ProtocolAdapter.MS.text(ret_str))
