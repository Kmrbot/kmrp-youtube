from nonebot import logger
from utils.KmrClientPy.KmrClient.client.web.request import request
from utils.KmrClientPy.KmrClient.message_marshal.marshal import set_marshal, MarshalType
from ..youtube_config import \
    get_youtube_api_key, \
    get_youtube_monitor_server_addr_port, \
    get_youtube_monitor_server_get_channel_info_entry, \
    get_youtube_monitor_server_get_vide_list_entry
from .protocol import YoutubeMonitor_pb2


def get_channel_info(channel_id: str):
    get_channel_info_req = YoutubeMonitor_pb2.WebGetChannelInfoReq()
    get_channel_info_req.serviceInfo.apiKey = get_youtube_api_key()
    # get_channel_info_req.serviceInfo.proxy = ""
    get_channel_info_req.channelID = channel_id
    get_channel_info_rsp = YoutubeMonitor_pb2.WebGetChannelInfoRsp()

    addr, port = get_youtube_monitor_server_addr_port()
    entry = get_youtube_monitor_server_get_channel_info_entry()

    set_marshal(MarshalType.MARSHAL_TYPE_PROTOJSON)
    is_success = request(addr, port, "POST", entry, get_channel_info_req, get_channel_info_rsp).start()
    if not is_success:
        logger.error(f"get_channel_info fail ! channel_id = {channel_id}")
        return
    if get_channel_info_rsp.result != 0:
        logger.error(f"get_channel_info channel_id = {channel_id} result = {get_channel_info_rsp.result } !")
        return
    return {
        "title": get_channel_info_rsp.title,
        "description": get_channel_info_rsp.description,
        "publish_timestamp": get_channel_info_rsp.publishTimestamp,
        "country": get_channel_info_rsp.country,
        "playlist_id": get_channel_info_rsp.playlistID,
    }


def get_video_list(channel_id: str, playlist_id: str):
    get_video_list_req = YoutubeMonitor_pb2.WebGetVideoListReq()
    get_video_list_req.serviceInfo.apiKey = get_youtube_api_key()
    # get_video_list_req.serviceInfo.proxy = ""
    get_video_list_req.playListID = playlist_id
    get_video_list_req.maxResults = 20
    get_video_list_rsp = YoutubeMonitor_pb2.WebGetVideoListRsp()

    addr, port = get_youtube_monitor_server_addr_port()
    entry = get_youtube_monitor_server_get_vide_list_entry()

    set_marshal(MarshalType.MARSHAL_TYPE_PROTOJSON)
    is_success = request(addr, port, "POST", entry, get_video_list_req, get_video_list_rsp).start()
    if not is_success:
        logger.error(f"get_video_list fail ! channel_id = {channel_id} playlist_id = {playlist_id}")
        return None
    if get_video_list_rsp.result != 0:
        logger.error(f"get_video_list channel_id = {channel_id} result = {get_video_list_rsp.result } !")
        return None
    return {
        "videos": get_video_list_rsp.videos,
        "nextPageToken": get_video_list_rsp.nextPageToken,
        "prePageToken": get_video_list_rsp.prePageToken,
    }
