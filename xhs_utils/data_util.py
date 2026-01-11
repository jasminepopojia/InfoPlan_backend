import json
import os
import re
import time
import openpyxl
import requests
from loguru import logger
from retry import retry


def norm_str(str):
    new_str = re.sub(r"|[\\/:*?\"<>| ]+", "", str).replace('\n', '').replace('\r', '')
    return new_str

def norm_text(text):
    ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')
    text = ILLEGAL_CHARACTERS_RE.sub(r'', text)
    return text


def timestamp_to_str(timestamp):
    time_local = time.localtime(timestamp / 1000)
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
    return dt

def handle_user_info(data, user_id):
    home_url = f'https://www.xiaohongshu.com/user/profile/{user_id}'
    nickname = data['basic_info']['nickname']
    avatar = data['basic_info']['imageb']
    red_id = data['basic_info']['red_id']
    gender = data['basic_info']['gender']
    if gender == 0:
        gender = '男'
    elif gender == 1:
        gender = '女'
    else:
        gender = '未知'
    ip_location = data['basic_info']['ip_location']
    desc = data['basic_info']['desc']
    follows = data['interactions'][0]['count']
    fans = data['interactions'][1]['count']
    interaction = data['interactions'][2]['count']
    tags_temp = data['tags']
    tags = []
    for tag in tags_temp:
        try:
            tags.append(tag['name'])
        except:
            pass
    return {
        'user_id': user_id,
        'home_url': home_url,
        'nickname': nickname,
        'avatar': avatar,
        'red_id': red_id,
        'gender': gender,
        'ip_location': ip_location,
        'desc': desc,
        'follows': follows,
        'fans': fans,
        'interaction': interaction,
        'tags': tags,
    }

# def handle_note_info(data):
#     note_id = data['id']
#     note_url = data['url']
#     note_type = data['note_card']['type']
#     if note_type == 'normal':
#         note_type = '图集'
#     else:
#         note_type = '视频'
#     user_id = data['note_card']['user']['user_id']
#     home_url = f'https://www.xiaohongshu.com/user/profile/{user_id}'
#     nickname = data['note_card']['user']['nickname']
#     avatar = data['note_card']['user']['avatar']
#     title = data['note_card']['title']
#     if title.strip() == '':
#         title = f'无标题'
#     desc = data['note_card']['desc']
#     liked_count = data['note_card']['interact_info']['liked_count']
#     collected_count = data['note_card']['interact_info']['collected_count']
#     comment_count = data['note_card']['interact_info']['comment_count']
#     share_count = data['note_card']['interact_info']['share_count']
#     image_list_temp = data['note_card']['image_list']
#     image_list = []
#     for image in image_list_temp:
#         try:
#             image_list.append(image['info_list'][1]['url'])
#             # success, msg, img_url = XHS_Apis.get_note_no_water_img(image['info_list'][1]['url'])
#             # image_list.append(img_url)
#         except:
#             pass
#     if note_type == '视频':
#         video_cover = image_list[0]
#         video_addr = 'https://sns-video-bd.xhscdn.com/' + data['note_card']['video']['consumer']['origin_video_key']
#         # success, msg, video_addr = XHS_Apis.get_note_no_water_video(note_id)
#     else:
#         video_cover = None
#         video_addr = None
#     tags_temp = data['note_card']['tag_list']
#     tags = []
#     for tag in tags_temp:
#         try:
#             tags.append(tag['name'])
#         except:
#             pass
#     upload_time = timestamp_to_str(data['note_card']['time'])
#     if 'ip_location' in data['note_card']:
#         ip_location = data['note_card']['ip_location']
#     else:
#         ip_location = '未知'
#     return {
#         'note_id': note_id,
#         'note_url': note_url,
#         'note_type': note_type,
#         'user_id': user_id,
#         'home_url': home_url,
#         'nickname': nickname,
#         'avatar': avatar,
#         'title': title,
#         'desc': desc,
#         'liked_count': liked_count,
#         'collected_count': collected_count,
#         'comment_count': comment_count,
#         'share_count': share_count,
#         'video_cover': video_cover,
#         'video_addr': video_addr,
#         'image_list': image_list,
#         'tags': tags,
#         'upload_time': upload_time,
#         'ip_location': ip_location,
#     }

def handle_note_info(data):
    """
    处理笔记信息，支持图集和视频两种类型
    """
    note_id = data['id']
    note_url = data.get('url', '')
    note_type = data['note_card']['type']
    
    if note_type == 'normal':
        note_type = '图集'
    else:
        note_type = '视频'
    
    user_id = data['note_card']['user']['user_id']
    home_url = f'https://www.xiaohongshu.com/user/profile/{user_id}'
    nickname = data['note_card']['user']['nickname']
    avatar = data['note_card']['user']['avatar']
    title = data['note_card']['title']
    if title.strip() == '':
        title = f'无标题'
    desc = data['note_card']['desc']
    liked_count = data['note_card']['interact_info']['liked_count']
    collected_count = data['note_card']['interact_info']['collected_count']
    comment_count = data['note_card']['interact_info']['comment_count']
    share_count = data['note_card']['interact_info']['share_count']
    
    # 处理图片列表
    image_list_temp = data['note_card'].get('image_list', [])
    image_list = []
    for image in image_list_temp:
        try:
            # 优先使用 info_list[1] (WB_DFT)，如果没有则使用 info_list[0] (WB_PRV)
            if 'info_list' in image and len(image['info_list']) > 0:
                # 查找 WB_DFT 格式的图片
                for info in image['info_list']:
                    if info.get('image_scene') == 'WB_DFT':
                        image_list.append(info['url'])
                        break
                else:
                    # 如果没有 WB_DFT，使用第一个可用的
                    image_list.append(image['info_list'][0]['url'])
            elif 'url_default' in image and image['url_default']:
                image_list.append(image['url_default'])
        except Exception as e:
            logger.warning(f"处理图片时出错: {e}")
            pass
    
    # 处理视频相关数据
    video_cover = None
    video_addr = None
    video_duration = None
    video_streams = []  # 存储所有可用的视频流信息
    
    if note_type == '视频':
        try:
            video_data = data['note_card'].get('video', {})
            
            # 获取视频封面
            if image_list:
                video_cover = image_list[0]
            elif 'image' in video_data:
                # 尝试从 video.image 获取封面
                thumbnail_fileid = video_data['image'].get('thumbnail_fileid', '')
                if thumbnail_fileid:
                    video_cover = f"https://sns-webpic-qc.xhscdn.com/{thumbnail_fileid}"
            
            # 获取视频时长
            if 'capa' in video_data and 'duration' in video_data['capa']:
                video_duration = video_data['capa']['duration']  # 单位：秒
            
            # 获取视频链接（优先选择最高质量的）
            if 'media' in video_data and 'stream' in video_data['media']:
                stream_data = video_data['media']['stream']
                
                # 按优先级选择：h265 > h264 > av1 > h266
                video_streams_list = []
                
                # 收集所有可用的视频流
                for codec_type in ['h265', 'h264', 'av1', 'h266']:
                    if codec_type in stream_data and stream_data[codec_type]:
                        for stream in stream_data[codec_type]:
                            if 'master_url' in stream:
                                video_streams_list.append({
                                    'url': stream['master_url'],
                                    'backup_urls': stream.get('backup_urls', []),
                                    'codec': codec_type,
                                    'quality': stream.get('quality_type', 'Unknown'),
                                    'width': stream.get('width', 0),
                                    'height': stream.get('height', 0),
                                    'size': stream.get('size', 0),
                                    'duration': stream.get('duration', 0),
                                    'bitrate': stream.get('avg_bitrate', 0)
                                })
                
                # 选择最高质量的视频（优先选择分辨率最高的）
                if video_streams_list:
                    # 按分辨率排序，选择最高的
                    video_streams_list.sort(key=lambda x: x['width'] * x['height'], reverse=True)
                    best_stream = video_streams_list[0]
                    video_addr = best_stream['url']
                    video_streams = video_streams_list  # 保存所有可用的流
                    
                    logger.info(f"选择视频流: {best_stream['codec']}, 分辨率: {best_stream['width']}x{best_stream['height']}, 质量: {best_stream['quality']}")
                else:
                    logger.warning("未找到可用的视频流")
            
            # 兼容旧的数据格式（如果新格式没有找到）
            if not video_addr and 'consumer' in video_data:
                try:
                    origin_video_key = video_data['consumer'].get('origin_video_key', '')
                    if origin_video_key:
                        video_addr = 'https://sns-video-bd.xhscdn.com/' + origin_video_key
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"处理视频数据时出错: {e}", exc_info=True)
            video_cover = image_list[0] if image_list else None
            video_addr = None
    
    # 处理标签
    tags_temp = data['note_card'].get('tag_list', [])
    tags = []
    for tag in tags_temp:
        try:
            tags.append(tag['name'])
        except:
            pass
    
    # 处理上传时间
    upload_time = timestamp_to_str(data['note_card']['time'])
    
    # 处理IP位置
    if 'ip_location' in data['note_card']:
        ip_location = data['note_card']['ip_location']
    else:
        ip_location = '未知'
    
    # 构建返回数据
    result = {
        'note_id': note_id,
        'note_url': note_url,
        'note_type': note_type,
        'user_id': user_id,
        'home_url': home_url,
        'nickname': nickname,
        'avatar': avatar,
        'title': title,
        'desc': desc,
        'liked_count': liked_count,
        'collected_count': collected_count,
        'comment_count': comment_count,
        'share_count': share_count,
        'video_cover': video_cover,
        'video_addr': video_addr,
        'video_duration': video_duration,  # 新增：视频时长
        'video_streams': video_streams,  # 新增：所有可用的视频流
        'image_list': image_list,
        'tags': tags,
        'upload_time': upload_time,
        'ip_location': ip_location,
    }
    
    return result

def handle_comment_info(data):
    note_id = data['note_id']
    note_url = data['note_url']
    comment_id = data['id']
    user_id = data['user_info']['user_id']
    home_url = f'https://www.xiaohongshu.com/user/profile/{user_id}'
    nickname = data['user_info']['nickname']
    avatar = data['user_info']['image']
    content = data['content']
    show_tags = data['show_tags']
    like_count = data['like_count']
    upload_time = timestamp_to_str(data['create_time'])
    try:
        ip_location = data['ip_location']
    except:
        ip_location = '未知'
    pictures = []
    try:
        pictures_temp = data['pictures']
        for picture in pictures_temp:
            try:
                pictures.append(picture['info_list'][1]['url'])
                # success, msg, img_url = XHS_Apis.get_note_no_water_img(picture['info_list'][1]['url'])
                # pictures.append(img_url)
            except:
                pass
    except:
        pass
    return {
        'note_id': note_id,
        'note_url': note_url,
        'comment_id': comment_id,
        'user_id': user_id,
        'home_url': home_url,
        'nickname': nickname,
        'avatar': avatar,
        'content': content,
        'show_tags': show_tags,
        'like_count': like_count,
        'upload_time': upload_time,
        'ip_location': ip_location,
        'pictures': pictures,
    }
def save_to_xlsx(datas, file_path, type='note'):
    wb = openpyxl.Workbook()
    ws = wb.active
    if type == 'note':
        headers = ['笔记id', '笔记url', '笔记类型', '用户id', '用户主页url', '昵称', '头像url', '标题', '描述', '点赞数量', '收藏数量', '评论数量', '分享数量', '视频封面url', '视频地址url', '图片地址url列表', '标签', '上传时间', 'ip归属地']
    elif type == 'user':
        headers = ['用户id', '用户主页url', '用户名', '头像url', '小红书号', '性别', 'ip地址', '介绍', '关注数量', '粉丝数量', '作品被赞和收藏数量', '标签']
    else:
        headers = ['笔记id', '笔记url', '评论id', '用户id', '用户主页url', '昵称', '头像url', '评论内容', '评论标签', '点赞数量', '上传时间', 'ip归属地', '图片地址url列表']
    ws.append(headers)
    for data in datas:
        data = {k: norm_text(str(v)) for k, v in data.items()}
        ws.append(list(data.values()))
    wb.save(file_path)
    logger.info(f'数据保存至 {file_path}')

def download_media(path, name, url, type):
    if type == 'image':
        content = requests.get(url).content
        with open(path + '/' + name + '.jpg', mode="wb") as f:
            f.write(content)
    elif type == 'video':
        res = requests.get(url, stream=True)
        size = 0
        chunk_size = 1024 * 1024
        with open(path + '/' + name + '.mp4', mode="wb") as f:
            for data in res.iter_content(chunk_size=chunk_size):
                f.write(data)
                size += len(data)

def save_user_detail(user, path):
    with open(f'{path}/detail.txt', mode="w", encoding="utf-8") as f:
        # 逐行输出到txt里
        f.write(f"用户id: {user['user_id']}\n")
        f.write(f"用户主页url: {user['home_url']}\n")
        f.write(f"用户名: {user['nickname']}\n")
        f.write(f"头像url: {user['avatar']}\n")
        f.write(f"小红书号: {user['red_id']}\n")
        f.write(f"性别: {user['gender']}\n")
        f.write(f"ip地址: {user['ip_location']}\n")
        f.write(f"介绍: {user['desc']}\n")
        f.write(f"关注数量: {user['follows']}\n")
        f.write(f"粉丝数量: {user['fans']}\n")
        f.write(f"作品被赞和收藏数量: {user['interaction']}\n")
        f.write(f"标签: {user['tags']}\n")

def save_note_detail(note, path):
    with open(f'{path}/detail.txt', mode="w", encoding="utf-8") as f:
        # 逐行输出到txt里
        f.write(f"笔记id: {note['note_id']}\n")
        f.write(f"笔记url: {note['note_url']}\n")
        f.write(f"笔记类型: {note['note_type']}\n")
        f.write(f"用户id: {note['user_id']}\n")
        f.write(f"用户主页url: {note['home_url']}\n")
        f.write(f"昵称: {note['nickname']}\n")
        f.write(f"头像url: {note['avatar']}\n")
        f.write(f"标题: {note['title']}\n")
        f.write(f"描述: {note['desc']}\n")
        f.write(f"点赞数量: {note['liked_count']}\n")
        f.write(f"收藏数量: {note['collected_count']}\n")
        f.write(f"评论数量: {note['comment_count']}\n")
        f.write(f"分享数量: {note['share_count']}\n")
        f.write(f"视频封面url: {note['video_cover']}\n")
        f.write(f"视频地址url: {note['video_addr']}\n")
        f.write(f"图片地址url列表: {note['image_list']}\n")
        f.write(f"标签: {note['tags']}\n")
        f.write(f"上传时间: {note['upload_time']}\n")
        f.write(f"ip归属地: {note['ip_location']}\n")



@retry(tries=3, delay=1)
def download_note(note_info, path, save_choice):
    handle_info_dir = os.path.abspath('download_note_info')
    os.makedirs(handle_info_dir, exist_ok=True)

    handle_path = os.path.join(handle_info_dir, f'note_{1}.json')
    with open(handle_path, 'w', encoding='utf-8') as f:
        json.dump(note_info, f, ensure_ascii=False, indent=2)
    logger.info(f'笔记信息已保存到 download_note_info: {handle_path}')

    note_id = note_info['note_id']
    user_id = note_info['user_id']
    title = note_info['title']
    title = norm_str(title)[:40]
    nickname = note_info['nickname']
    nickname = norm_str(nickname)[:20]
    if title.strip() == '':
        title = f'无标题'
    save_path = f'{path}/{nickname}_{user_id}/{title}_{note_id}'
    check_and_create_path(save_path)
    with open(f'{save_path}/info.json', mode='w', encoding='utf-8') as f:
        f.write(json.dumps(note_info) + '\n')
    note_type = note_info['note_type']
    save_note_detail(note_info, save_path)
    if note_type == '图集' and save_choice in ['media', 'media-image', 'all']:
        for img_index, img_url in enumerate(note_info['image_list']):
            download_media(save_path, f'image_{img_index}', img_url, 'image')
    elif note_type == '视频' and save_choice in ['media', 'media-video', 'all']:
        download_media(save_path, 'cover', note_info['video_cover'], 'image')
        download_media(save_path, 'video', note_info['video_addr'], 'video')
    return save_path


def check_and_create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)
