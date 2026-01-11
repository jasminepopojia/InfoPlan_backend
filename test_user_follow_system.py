"""
用户关注系统测试代码
模拟用户搜索、关注、获取笔记的完整流程
"""

import requests
import json
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger

# 配置
API_BASE_URL = "http://localhost:5001"
TIMEOUT = 60

# 配置日志
logger.add("test_user_follow.log", rotation="10 MB", retention="7 days")


class UserFollowSystem:
    """用户关注系统（内存存储版本，用于测试）"""
    
    def __init__(self, api_base_url: str = API_BASE_URL):
        self.api_base_url = api_base_url.rstrip('/')
        
        # 模拟数据库：用户表（实际应用中应该是数据库）
        # 格式: {user_id: {user_info}}
        self.users = {}
        
        # 模拟数据库：关注关系表
        # 格式: {app_user_id: [xhs_user_id1, xhs_user_id2, ...]}
        self.follows = {}
        
        # 模拟数据库：小红书用户信息表
        # 格式: {xhs_user_id: {完整的用户信息，包括xsec_token}}
        self.xhs_users = {}
    
    def search_xhs_users(self, keyword: str, page: int = 1) -> Dict:
        """
        搜索小红书用户
        :param keyword: 搜索关键词
        :param page: 页码
        :return: 搜索结果
        """
        try:
            url = f"{self.api_base_url}/api/search/user"
            payload = {
                "query": keyword,
                "page": page
            }
            
            logger.info(f"搜索小红书用户: keyword={keyword}, page={page}")
            response = requests.post(url, json=payload, timeout=TIMEOUT)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    users = result.get('data', {}).get('users', [])
                    logger.info(f"✅ 搜索成功，找到 {len(users)} 个用户")
                    return {
                        "success": True,
                        "users": users,
                        "count": len(users)
                    }
                else:
                    logger.error(f"搜索失败: {result.get('msg')}")
                    return {
                        "success": False,
                        "msg": result.get('msg'),
                        "users": []
                    }
            else:
                logger.error(f"请求失败: HTTP {response.status_code}")
                return {
                    "success": False,
                    "msg": f"HTTP {response.status_code}",
                    "users": []
                }
                
        except Exception as e:
            logger.error(f"搜索用户异常: {e}", exc_info=True)
            return {
                "success": False,
                "msg": str(e),
                "users": []
            }
    
    def follow_xhs_user(self, app_user_id: str, xhs_user_info: Dict) -> Dict:
        """
        关注小红书用户
        :param app_user_id: 应用用户ID
        :param xhs_user_info: 小红书用户信息（从搜索结果中获取）
        :return: 关注结果
        """
        try:
            xhs_user_id = xhs_user_info.get('id')
            if not xhs_user_id:
                return {
                    "success": False,
                    "msg": "用户ID不存在"
                }
            
            # 检查是否已经关注
            if app_user_id in self.follows:
                if xhs_user_id in self.follows[app_user_id]:
                    logger.warning(f"用户 {app_user_id} 已经关注了 {xhs_user_id}")
                    return {
                        "success": False,
                        "msg": "已经关注过该用户"
                    }
            else:
                self.follows[app_user_id] = []
            
            # 存储小红书用户完整信息（包括xsec_token）
            user_data = {
                "id": xhs_user_info.get('id'),
                "name": xhs_user_info.get('name'),
                "red_id": xhs_user_info.get('red_id'),
                "fans": xhs_user_info.get('fans'),
                "note_count": xhs_user_info.get('note_count'),
                "image": xhs_user_info.get('image'),
                "sub_title": xhs_user_info.get('sub_title'),
                "xsec_token": xhs_user_info.get('xsec_token', ''),  # 重要：存储xsec_token
                "followed": xhs_user_info.get('followed', False),
                "update_time": xhs_user_info.get('update_time'),
                "created_at": datetime.now().isoformat(),  # 关注时间
                "user_url": self._build_user_url(xhs_user_id, xhs_user_info.get('xsec_token', ''))
            }
            
            # 保存到"数据库"
            self.xhs_users[xhs_user_id] = user_data
            self.follows[app_user_id].append(xhs_user_id)
            
            logger.info(f"✅ 用户 {app_user_id} 成功关注 {xhs_user_id} ({user_data.get('name')})")
            
            return {
                "success": True,
                "msg": "关注成功",
                "user_info": user_data
            }
            
        except Exception as e:
            logger.error(f"关注用户异常: {e}", exc_info=True)
            return {
                "success": False,
                "msg": str(e)
            }
    
    def _build_user_url(self, xhs_user_id: str, xsec_token: str) -> str:
        """
        构建用户完整URL
        :param xhs_user_id: 小红书用户ID
        :param xsec_token: xsec_token
        :return: 完整的用户URL
        """
        base_url = f"https://www.xiaohongshu.com/user/profile/{xhs_user_id}"
        if xsec_token:
            return f"{base_url}?xsec_token={xsec_token}&xsec_source=pc_search"
        return base_url
    
    def get_followed_users(self, app_user_id: str) -> List[Dict]:
        """
        获取用户关注的小红书用户列表
        :param app_user_id: 应用用户ID
        :return: 关注列表
        """
        if app_user_id not in self.follows:
            return []
        
        followed_list = []
        for xhs_user_id in self.follows[app_user_id]:
            if xhs_user_id in self.xhs_users:
                followed_list.append(self.xhs_users[xhs_user_id])
        
        return followed_list
    
    def get_user_notes(self, app_user_id: str, xhs_user_id: str, limit: int = 20) -> Dict:
        """
        获取关注用户的所有笔记
        :param app_user_id: 应用用户ID
        :param xhs_user_id: 小红书用户ID
        :param limit: 限制返回数量
        :return: 笔记列表
        """
        try:
            # 检查是否关注
            if app_user_id not in self.follows or xhs_user_id not in self.follows[app_user_id]:
                return {
                    "success": False,
                    "msg": "未关注该用户"
                }
            
            # 获取存储的用户信息（包含xsec_token）
            if xhs_user_id not in self.xhs_users:
                return {
                    "success": False,
                    "msg": "用户信息不存在"
                }
            
            xhs_user_info = self.xhs_users[xhs_user_id]
            user_url = xhs_user_info.get('user_url')
            
            if not user_url:
                # 如果没有存储URL，尝试构建
                user_url = self._build_user_url(
                    xhs_user_id,
                    xhs_user_info.get('xsec_token', '')
                )
            
            logger.info(f"获取用户笔记: {xhs_user_id}, URL: {user_url}")
            
            # 调用API获取笔记
            url = f"{self.api_base_url}/api/user/notes/{xhs_user_id}"
            params = {"limit": limit}
            
            response = requests.get(url, params=params, timeout=TIMEOUT)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    notes = result.get('data', {}).get('notes', [])
                    logger.info(f"✅ 成功获取 {len(notes)} 条笔记")
                    return {
                        "success": True,
                        "notes": notes,
                        "count": len(notes),
                        "user_info": xhs_user_info
                    }
                else:
                    # 如果API调用失败，尝试使用存储的URL直接调用
                    logger.warning(f"API调用失败，尝试使用存储的URL: {result.get('msg')}")
                    return self._get_notes_by_url(user_url, limit)
            else:
                return {
                    "success": False,
                    "msg": f"HTTP {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"获取笔记异常: {e}", exc_info=True)
            return {
                "success": False,
                "msg": str(e)
            }
    
    def _get_notes_by_url(self, user_url: str, limit: int) -> Dict:
        """
        通过完整URL获取笔记（备用方法）
        """
        try:
            # 这里可以直接调用爬虫API，使用存储的完整URL
            # 由于api_server.py中的接口需要user_id，我们可以解析URL
            from urllib.parse import urlparse, parse_qs
            
            parsed = urlparse(user_url)
            user_id = parsed.path.split('/')[-1]
            
            # 调用API（这里可能需要修改api_server.py支持直接传入完整URL）
            # 暂时返回错误，提示需要改进API
            return {
                "success": False,
                "msg": "需要使用存储的完整URL调用爬虫API",
                "user_url": user_url
            }
        except Exception as e:
            return {
                "success": False,
                "msg": str(e)
            }
    
    def unfollow_xhs_user(self, app_user_id: str, xhs_user_id: str) -> Dict:
        """
        取消关注
        :param app_user_id: 应用用户ID
        :param xhs_user_id: 小红书用户ID
        :return: 取消关注结果
        """
        try:
            if app_user_id not in self.follows:
                return {
                    "success": False,
                    "msg": "用户不存在"
                }
            
            if xhs_user_id not in self.follows[app_user_id]:
                return {
                    "success": False,
                    "msg": "未关注该用户"
                }
            
            self.follows[app_user_id].remove(xhs_user_id)
            logger.info(f"✅ 用户 {app_user_id} 取消关注 {xhs_user_id}")
            
            return {
                "success": True,
                "msg": "取消关注成功"
            }
            
        except Exception as e:
            logger.error(f"取消关注异常: {e}", exc_info=True)
            return {
                "success": False,
                "msg": str(e)
            }


def test_complete_flow():
    """完整流程测试"""
    print("=" * 70)
    print("  用户关注系统测试")
    print("=" * 70)
    
    # 初始化系统
    system = UserFollowSystem()
    
    # 模拟应用用户ID
    app_user_id = "test_user_001"
    
    # ========== 步骤1: 搜索小红书用户 ==========
    print("\n" + "=" * 70)
    print("步骤1: 搜索小红书用户")
    print("=" * 70)
    
    keyword = "美食"
    search_result = system.search_xhs_users(keyword, page=1)
    
    if not search_result.get('success'):
        print(f"❌ 搜索失败: {search_result.get('msg')}")
        return
    
    users = search_result.get('users', [])
    print(f"\n✅ 搜索成功，找到 {len(users)} 个用户\n")
    
    # 显示搜索结果
    for i, user in enumerate(users[:5], 1):  # 只显示前5个
        print(f"{i}. {user.get('name', 'N/A')}")
        print(f"   用户ID: {user.get('id', 'N/A')}")
        print(f"   小红书号: {user.get('red_id', 'N/A')}")
        print(f"   粉丝数: {user.get('fans', 'N/A')}")
        print(f"   笔记数: {user.get('note_count', 'N/A')}")
        print(f"   xsec_token: {user.get('xsec_token', 'N/A')[:30]}..." if user.get('xsec_token') else "   xsec_token: 无")
        print()
    
    if not users:
        print("⚠️ 没有找到用户，测试结束")
        return
    
    # ========== 步骤2: 选择关注用户 ==========
    print("\n" + "=" * 70)
    print("步骤2: 关注用户")
    print("=" * 70)
    
    # 选择第一个用户进行关注
    selected_user = users[0]
    follow_result = system.follow_xhs_user(app_user_id, selected_user)
    
    if follow_result.get('success'):
        user_info = follow_result.get('user_info', {})
        print(f"\n✅ 关注成功!")
        print(f"   用户: {user_info.get('name')}")
        print(f"   用户ID: {user_info.get('id')}")
        print(f"   完整URL: {user_info.get('user_url')}")
        print(f"   xsec_token: {user_info.get('xsec_token', '')[:30]}..." if user_info.get('xsec_token') else "   xsec_token: 无")
    else:
        print(f"\n❌ 关注失败: {follow_result.get('msg')}")
        return
    
    # 再关注一个用户（测试多个关注）
    if len(users) > 1:
        follow_result2 = system.follow_xhs_user(app_user_id, users[1])
        if follow_result2.get('success'):
            print(f"\n✅ 同时关注了第二个用户: {users[1].get('name')}")
    
    # ========== 步骤3: 查看关注列表 ==========
    print("\n" + "=" * 70)
    print("步骤3: 查看关注列表")
    print("=" * 70)
    
    followed_list = system.get_followed_users(app_user_id)
    print(f"\n✅ 当前关注了 {len(followed_list)} 个用户:\n")
    
    for i, user in enumerate(followed_list, 1):
        print(f"{i}. {user.get('name')}")
        print(f"   用户ID: {user.get('id')}")
        print(f"   完整URL: {user.get('user_url')}")
        print(f"   关注时间: {user.get('created_at')}")
        print()
    
    # ========== 步骤4: 获取关注用户的笔记 ==========
    print("\n" + "=" * 70)
    print("步骤4: 获取关注用户的笔记")
    print("=" * 70)
    
    if followed_list:
        xhs_user_id = followed_list[0].get('id')
        notes_result = system.get_user_notes(app_user_id, xhs_user_id, limit=5)
        
        if notes_result.get('success'):
            notes = notes_result.get('notes', [])
            print(f"\n✅ 成功获取 {len(notes)} 条笔记\n")
            
            for i, note in enumerate(notes, 1):
                print(f"{i}. {note.get('title', '无标题')[:50]}")
                print(f"   笔记ID: {note.get('note_id', 'N/A')}")
                print(f"   类型: {note.get('type', 'N/A')}")
                if note.get('note_url'):
                    print(f"   笔记URL: {note.get('note_url')}")
                print()
        else:
            print(f"\n❌ 获取笔记失败: {notes_result.get('msg')}")
            if notes_result.get('user_url'):
                print(f"   提示: 需要使用存储的URL: {notes_result.get('user_url')}")
    
    # ========== 步骤5: 取消关注 ==========
    print("\n" + "=" * 70)
    print("步骤5: 取消关注（可选测试）")
    print("=" * 70)
    
    if followed_list:
        xhs_user_id = followed_list[0].get('id')
        unfollow_result = system.unfollow_xhs_user(app_user_id, xhs_user_id)
        
        if unfollow_result.get('success'):
            print(f"\n✅ 取消关注成功")
            print(f"   当前关注数: {len(system.get_followed_users(app_user_id))}")
        else:
            print(f"\n❌ 取消关注失败: {unfollow_result.get('msg')}")
    
    # ========== 显示存储的数据结构 ==========
    print("\n" + "=" * 70)
    print("数据结构预览（模拟数据库）")
    print("=" * 70)
    print(f"\n关注关系表 (follows):")
    print(json.dumps(system.follows, ensure_ascii=False, indent=2))
    print(f"\n小红书用户信息表 (xhs_users) - 前1条:")
    if system.xhs_users:
        first_user_id = list(system.xhs_users.keys())[0]
        user_data = system.xhs_users[first_user_id].copy()
        # 隐藏敏感信息
        if 'xsec_token' in user_data:
            user_data['xsec_token'] = user_data['xsec_token'][:30] + "..."
        print(json.dumps({first_user_id: user_data}, ensure_ascii=False, indent=2))
    
    print("\n" + "=" * 70)
    print("测试完成!")
    print("=" * 70)


if __name__ == "__main__":
    test_complete_flow()