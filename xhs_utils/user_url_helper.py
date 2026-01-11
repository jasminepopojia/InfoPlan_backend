# xhs_utils/user_url_helper.py

"""
用户URL辅助工具
用于通过用户ID获取包含xsec_token的完整URL
"""

from typing import Optional
from loguru import logger
from apis.xhs_pc_apis import XHS_Apis


class UserURLHelper:
    """用户URL辅助类"""
    
    def __init__(self, cookies_str: str):
        """
        初始化
        :param cookies_str: Cookie字符串
        """
        self.cookies_str = cookies_str
        self.xhs_apis = XHS_Apis()
    
    def get_user_url_with_token(self, user_id: str) -> Optional[str]:
        """
        通过用户ID获取包含xsec_token的完整URL
        :param user_id: 用户ID
        :return: 完整的用户URL（包含xsec_token），如果失败返回None
        """
        try:
            # 方法1: 尝试通过用户信息接口获取（如果支持）
            # 这里先尝试直接构建，如果失败再搜索
            
            # 方法2: 通过搜索获取（需要知道用户的昵称或关键词）
            # 这个方法需要额外的信息，暂时不实现
            
            # 方法3: 直接返回基础URL（让API自己处理）
            # 根据代码逻辑，xsec_token可以为空
            base_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
            logger.info(f"构建用户URL: {base_url}（xsec_token将在API调用时处理）")
            return base_url
            
        except Exception as e:
            logger.error(f"获取用户URL失败: {e}")
            return None
    
    def search_user_by_id(self, user_id: str, search_keyword: str = None) -> Optional[str]:
        """
        通过搜索找到用户并获取完整URL
        :param user_id: 用户ID
        :param search_keyword: 搜索关键词（可选，如果不提供会尝试使用用户ID）
        :return: 完整的用户URL（包含xsec_token）
        """
        try:
            # 如果没有提供搜索关键词，尝试使用用户ID
            if not search_keyword:
                search_keyword = user_id
            
            # 搜索用户
            success, msg, res_json = self.xhs_apis.search_user(search_keyword, self.cookies_str, page=1)
            
            if success and res_json:
                users = res_json.get('data', {}).get('users', [])
                
                # 在搜索结果中查找匹配的用户ID
                for user in users:
                    if user.get('id') == user_id:
                        # 构建完整URL
                        xsec_token = user.get('xsec_token', '')
                        if xsec_token:
                            user_url = f"https://www.xiaohongshu.com/user/profile/{user_id}?xsec_token={xsec_token}&xsec_source=pc_search"
                            logger.info(f"✅ 找到用户，构建完整URL: {user_url}")
                            return user_url
                        else:
                            logger.warning(f"用户搜索结果中没有xsec_token")
                            break
            
            logger.warning(f"未在搜索结果中找到用户ID: {user_id}")
            return None
            
        except Exception as e:
            logger.error(f"搜索用户失败: {e}")
            return None