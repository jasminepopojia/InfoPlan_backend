# test_local_api.py（改进版）

"""
本地API接口测试脚本（改进版）
支持通过搜索获取xsec_token，提高测试成功率
"""

import requests
import json
import time
from typing import Dict, Any, Optional
from loguru import logger

# 配置
API_BASE_URL = "http://localhost:5001"
TIMEOUT = 60  # 请求超时时间（秒）

# 测试用的用户ID
TEST_USER_IDS = [
    "5fc5e92100000000010053a5",
    "5fcc82fa000000000101dc00"
]

# 配置日志
logger.add("test_local_api.log", rotation="10 MB", retention="7 days")


class LocalAPITester:
    """本地API测试类（改进版）"""
    
    # def __init__(self, base_url: str = API_BASE_URL, timeout: int = TIMEOUT):
    #     self.base_url = base_url.rstrip('/')
    #     self.timeout = timeout
    #     self.session = requests.Session()
    #     self.session.headers.update({
    #         'Content-Type': 'application/json',
    #         'Accept': 'application/json'
    #     })
    #     # 缓存用户URL（包含xsec_token）
    #     self.user_url_cache = {}

    def __init__(self, base_url: str = API_BASE_URL, timeout: int = TIMEOUT, disable_cache: bool = True):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.disable_cache = disable_cache  # 新增：是否禁用缓存
        
        # 创建session，禁用缓存
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Cache-Control': 'no-cache, no-store, must-revalidate',  # 禁用缓存
            'Pragma': 'no-cache',
            'Expires': '0'
        })
        
        # 缓存用户URL（如果不禁用缓存）
        self.user_url_cache = {}
    
    def print_section(self, title: str):
        """打印测试章节标题"""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)
    
    def print_result(self, success: bool, message: str, data: Any = None):
        """打印测试结果"""
        status = "✅" if success else "❌"
        print(f"\n{status} {message}")
        if data and isinstance(data, dict):
            if data.get('success'):
                print(f"   响应数据: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
            else:
                print(f"   错误信息: {data.get('msg', 'N/A')}")
    
    # def get_user_url_with_token(self, user_id: str, search_keyword: str = "美食") -> Optional[str]:
    #     """
    #     通过搜索获取包含xsec_token的用户URL
    #     :param user_id: 用户ID
    #     :param search_keyword: 搜索关键词
    #     :return: 完整的用户URL（包含xsec_token）
    #     """
    #     # 检查缓存
    #     if user_id in self.user_url_cache:
    #         return self.user_url_cache[user_id]
        
    #     try:
    #         # 搜索用户
    #         url = f"{self.base_url}/api/search/user"
    #         payload = {"query": search_keyword, "page": 1}
            
    #         response = self.session.post(url, json=payload, timeout=self.timeout)
            
    #         if response.status_code == 200:
    #             result = response.json()
    #             if result.get('success'):
    #                 users = result.get('data', {}).get('users', [])
                    
    #                 # 查找匹配的用户
    #                 for user in users:
    #                     if user.get('id') == user_id:
    #                         xsec_token = user.get('xsec_token', '')
    #                         if xsec_token:
    #                             full_url = f"https://www.xiaohongshu.com/user/profile/{user_id}?xsec_token={xsec_token}&xsec_source=pc_search"
    #                             self.user_url_cache[user_id] = full_url
    #                             logger.info(f"✅ 为用户 {user_id} 获取到完整URL")
    #                             return full_url
            
    #         # 如果搜索失败，返回基础URL
    #         base_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
    #         logger.warning(f"⚠️ 无法获取用户 {user_id} 的xsec_token，使用基础URL")
    #         return base_url
            
    #     except Exception as e:
    #         logger.error(f"获取用户URL失败: {e}")
    #         return f"https://www.xiaohongshu.com/user/profile/{user_id}"
    
    def test_health_check(self) -> bool:
        """测试1: 健康检查接口"""
        self.print_section("测试1: 健康检查接口")
        
        try:
            url = f"{self.base_url}/health"
            print(f"请求URL: {url}")
            
            response = self.session.get(url, timeout=5)
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
                self.print_result(True, "健康检查通过")
                return True
            else:
                self.print_result(False, f"健康检查失败: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            self.print_result(False, f"无法连接到服务器: {self.base_url}")
            print("   提示: 请确保api_server.py正在运行")
            return False
        except Exception as e:
            self.print_result(False, f"测试失败: {e}")
            return False
    
    def test_search_user(self, query: str = "美食", page: int = 1) -> Dict[str, Any]:
        """测试2: 搜索用户接口"""
        self.print_section("测试2: 搜索用户接口")
        
        try:
            url = f"{self.base_url}/api/search/user"
            payload = {
                "query": query,
                "page": page
            }
            
            print(f"请求URL: {url}")
            print(f"请求参数: {json.dumps(payload, ensure_ascii=False, indent=2)}")
            
            start_time = time.time()
            response = self.session.post(url, json=payload, timeout=self.timeout)
            elapsed_time = time.time() - start_time
            
            print(f"响应状态码: {response.status_code}")
            print(f"请求耗时: {elapsed_time:.2f}秒")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    users = result.get('data', {}).get('users', [])
                    print(f"\n✅ 搜索成功，找到 {len(users)} 个用户")
                    
                    # 显示前3个用户
                    if users:
                        print("\n前3个用户信息:")
                        for i, user in enumerate(users[:3], 1):
                            print(f"  {i}. {user.get('name', 'N/A')}")
                            print(f"     ID: {user.get('id', 'N/A')}")
                            print(f"     粉丝数: {user.get('fans', 'N/A')}")
                            print(f"     笔记数: {user.get('note_count', 'N/A')}")
                            print(f"     xsec_token: {user.get('xsec_token', 'N/A')[:30]}..." if user.get('xsec_token') else "     xsec_token: 无")
                            print()
                    
                    return result
                else:
                    self.print_result(False, f"搜索失败: {result.get('msg')}")
                    return result
            else:
                self.print_result(False, f"请求失败: HTTP {response.status_code}")
                print(f"响应内容: {response.text[:500]}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            self.print_result(False, f"测试失败: {e}")
            logger.error(f"搜索用户接口测试失败: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def test_search_user_batch(self, query: str = "美食", require_num: int = 5) -> Dict[str, Any]:
        """测试3: 批量搜索用户接口"""
        self.print_section("测试3: 批量搜索用户接口")
        
        try:
            url = f"{self.base_url}/api/search/user/batch"
            payload = {
                "query": query,
                "require_num": require_num
            }
            
            print(f"请求URL: {url}")
            print(f"请求参数: {json.dumps(payload, ensure_ascii=False, indent=2)}")
            
            start_time = time.time()
            response = self.session.post(url, json=payload, timeout=self.timeout)
            elapsed_time = time.time() - start_time
            
            print(f"响应状态码: {response.status_code}")
            print(f"请求耗时: {elapsed_time:.2f}秒")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    users = result.get('data', {}).get('users', [])
                    count = result.get('data', {}).get('count', 0)
                    print(f"\n✅ 批量搜索成功，找到 {count} 个用户")
                    
                    # 显示用户列表
                    if users:
                        print("\n用户列表:")
                        for i, user in enumerate(users[:5], 1):
                            print(f"  {i}. {user.get('name', 'N/A')} (ID: {user.get('id', 'N/A')})")
                    
                    return result
                else:
                    self.print_result(False, f"批量搜索失败: {result.get('msg')}")
                    return result
            else:
                self.print_result(False, f"请求失败: HTTP {response.status_code}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            self.print_result(False, f"测试失败: {e}")
            logger.error(f"批量搜索用户接口测试失败: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    

    def get_user_url_with_token(self, user_id: str, search_keyword: str = "美食", force_refresh: bool = False) -> Optional[str]:
        """
        通过搜索获取包含xsec_token的用户URL
        :param user_id: 用户ID
        :param search_keyword: 搜索关键词
        :param force_refresh: 强制刷新，不使用缓存
        :return: 完整的用户URL（包含xsec_token）
        """
        # 如果禁用缓存或强制刷新，跳过缓存检查
        if not self.disable_cache and not force_refresh:
            if user_id in self.user_url_cache:
                return self.user_url_cache[user_id]
        
        try:
            # 搜索用户（添加时间戳确保每次都是新请求）
            url = f"{self.base_url}/api/search/user"
            payload = {
                "query": search_keyword, 
                "page": 1,
                "_t": int(time.time() * 1000)  # 时间戳参数
            }
            
            # 使用GET请求时添加时间戳参数
            response = self.session.post(url, json=payload, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    users = result.get('data', {}).get('users', [])
                    
                    # 查找匹配的用户
                    for user in users:
                        if user.get('id') == user_id:
                            xsec_token = user.get('xsec_token', '')
                            if xsec_token:
                                full_url = f"https://www.xiaohongshu.com/user/profile/{user_id}?xsec_token={xsec_token}&xsec_source=pc_search"
                                
                                # 只有在不禁用缓存时才保存
                                if not self.disable_cache:
                                    self.user_url_cache[user_id] = full_url
                                
                                logger.info(f"✅ 为用户 {user_id} 获取到完整URL")
                                return full_url
            
            # 如果搜索失败，返回基础URL
            base_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"
            logger.warning(f"⚠️ 无法获取用户 {user_id} 的xsec_token，使用基础URL")
            return base_url
            
        except Exception as e:
            logger.error(f"获取用户URL失败: {e}")
            return f"https://www.xiaohongshu.com/user/profile/{user_id}"
    
    def test_get_user_notes_single(
        self, 
        user_id: str, 
        limit: int = 5, 
        search_keyword: str = None
    ) -> Dict[str, Any]:
        """
        测试4: 获取单个用户笔记接口（禁用缓存版本）
        """
        self.print_section(f"测试4: 获取单个用户笔记接口 (用户ID: {user_id})")
        
        try:
            url = f"{self.base_url}/api/user/notes/{user_id}"
            params = {
                "limit": limit,
                "_t": int(time.time() * 1000)  # 添加时间戳，确保每次都是新请求
            }
            
            # 如果提供了搜索关键词，添加到参数中
            if search_keyword:
                params["search_keyword"] = search_keyword
                print(f"使用搜索关键词获取xsec_token: {search_keyword}")
            
            print(f"请求URL: {url}")
            print(f"查询参数: {params}")
            
            start_time = time.time()
            response = self.session.get(url, params=params, timeout=self.timeout)
            elapsed_time = time.time() - start_time
            
            print(f"响应状态码: {response.status_code}")
            print(f"请求耗时: {elapsed_time:.2f}秒")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    notes = result.get('data', {}).get('notes', [])
                    count = result.get('data', {}).get('count', 0)
                    total = result.get('data', {}).get('total', 0)
                    
                    print(f"\n✅ 获取笔记成功")
                    print(f"   返回笔记数: {count}")
                    print(f"   用户总笔记数: {total}")
                    
                    # 显示笔记列表
                    if notes:
                        print("\n笔记列表:")
                        for i, note in enumerate(notes[:limit], 1):
                            title = note.get('title', 'N/A')[:50]
                            note_id = note.get('note_id', 'N/A')
                            note_type = note.get('type', 'N/A')
                            print(f"  {i}. {title}")
                            print(f"     笔记ID: {note_id}")
                            print(f"     类型: {note_type}")
                            print()
                    else:
                        print("   ⚠️ 笔记列表为空")
                    
                    return result
                else:
                    self.print_result(False, f"获取笔记失败: {result.get('msg')}")
                    print(f"   提示: {result.get('hint', '')}")
                    return result
            else:
                self.print_result(False, f"请求失败: HTTP {response.status_code}")
                print(f"响应内容: {response.text[:500]}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            self.print_result(False, f"测试失败: {e}")
            logger.error(f"获取单个用户笔记接口测试失败: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def test_get_users_notes(
        self, 
        user_ids: list = None, 
        max_users: int = 2, 
        notes_per_user: int = 3
    ) -> Dict[str, Any]:
        """测试5: 获取多个用户笔记接口（改进版）"""
        self.print_section("测试5: 获取多个用户笔记接口")
        
        if not user_ids:
            user_ids = TEST_USER_IDS[:max_users]
        
        try:
            url = f"{self.base_url}/api/users/notes"
            payload = {
                "user_ids": user_ids,
                "max_users": max_users,
                "notes_per_user": notes_per_user
            }
            
            print(f"请求URL: {url}")
            print(f"请求参数:")
            print(f"  用户ID列表: {user_ids}")
            print(f"  最多处理用户数: {max_users}")
            print(f"  每个用户笔记数: {notes_per_user}")
            
            start_time = time.time()
            response = self.session.post(url, json=payload, timeout=self.timeout * 2)
            elapsed_time = time.time() - start_time
            
            print(f"\n响应状态码: {response.status_code}")
            print(f"请求耗时: {elapsed_time:.2f}秒")
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('success'):
                    notes = result.get('data', {}).get('notes', [])
                    count = result.get('data', {}).get('count', 0)
                    users_processed = result.get('data', {}).get('users_processed', 0)
                    
                    print(f"\n✅ 获取笔记成功")
                    print(f"   处理用户数: {users_processed}")
                    print(f"   获取笔记数: {count}")
                    
                    # 显示笔记信息
                    if notes:
                        print("\n笔记详情（前10条）:")
                        for i, note in enumerate(notes[:10], 1):
                            title = note.get('title', 'N/A')
                            note_id = note.get('note_id', 'N/A')
                            user_id = note.get('user_id', 'N/A')
                            note_type = note.get('type', 'N/A')
                            
                            print(f"\n  {i}. {title[:60]}")
                            print(f"     笔记ID: {note_id}")
                            print(f"     用户ID: {user_id}")
                            print(f"     类型: {note_type}")
                            if note.get('url'):
                                print(f"     链接: {note.get('url')[:80]}...")
                    else:
                        print("\n   ⚠️ 未获取到笔记")
                    
                    return result
                else:
                    self.print_result(False, f"获取笔记失败: {result.get('msg')}")
                    print(f"   错误详情: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}")
                    return result
            else:
                self.print_result(False, f"请求失败: HTTP {response.status_code}")
                print(f"响应内容: {response.text[:500]}")
                return {"success": False, "error": response.text}
                
        except requests.exceptions.Timeout:
            self.print_result(False, f"请求超时（{self.timeout * 2}秒）")
            return {"success": False, "error": "请求超时"}
        except Exception as e:
            self.print_result(False, f"测试失败: {e}")
            logger.error(f"获取多个用户笔记接口测试失败: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def test_get_user_url_with_token(self, user_id: str, search_keyword: str = "美食") -> Dict[str, Any]:
        """
        测试6: 获取用户完整URL接口
        """
        self.print_section(f"测试6: 获取用户完整URL (用户ID: {user_id})")
        
        try:
            # 检查API是否提供此接口
            url = f"{self.base_url}/api/user/url/{user_id}"
            params = {"search_keyword": search_keyword}
            
            print(f"请求URL: {url}")
            print(f"查询参数: {params}")
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    full_url = result.get('data', {}).get('full_url', '')
                    print(f"\n✅ 获取用户URL成功")
                    print(f"   完整URL: {full_url}")
                    return result
                else:
                    self.print_result(False, f"获取URL失败: {result.get('msg')}")
                    return result
            elif response.status_code == 404:
                print(f"\n⚠️ API接口不存在，跳过此测试")
                return {"success": False, "error": "接口不存在"}
            else:
                self.print_result(False, f"请求失败: HTTP {response.status_code}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            print(f"\n⚠️ 测试失败或接口不存在: {e}")
            return {"success": False, "error": str(e)}
    
    def run_all_tests(self, use_search_token: bool = True):
        """
        运行所有测试
        :param use_search_token: 是否通过搜索获取xsec_token
        """
        print("=" * 70)
        print("  本地API接口测试（改进版）")
        print(f"  服务器地址: {self.base_url}")
        print(f"  使用搜索获取token: {'是' if use_search_token else '否'}")
        print("=" * 70)
        
        results = {}
        
        # 测试1: 健康检查
        results['health'] = self.test_health_check()
        
        if not results['health']:
            print("\n" + "=" * 70)
            print("  ❌ 健康检查失败，服务器可能未启动")
            print("  请先运行: python api_server.py")
            print("=" * 70)
            return results
        
        # 测试2: 搜索用户（用于获取xsec_token）
        search_result = self.test_search_user(query="美食", page=1)
        results['search_user'] = search_result
        
        # 如果搜索成功，尝试从结果中找到测试用户的xsec_token
        if use_search_token and search_result.get('success'):
            users = search_result.get('data', {}).get('users', [])
            for user in users:
                user_id = user.get('id')
                if user_id in TEST_USER_IDS:
                    xsec_token = user.get('xsec_token', '')
                    if xsec_token:
                        full_url = f"https://www.xiaohongshu.com/user/profile/{user_id}?xsec_token={xsec_token}&xsec_source=pc_search"
                        self.user_url_cache[user_id] = full_url
                        print(f"\n✅ 为测试用户 {user_id} 缓存了完整URL")
        
        # 测试3: 批量搜索用户
        results['search_user_batch'] = self.test_search_user_batch(query="美食", require_num=5)
        
        # 测试4: 获取单个用户笔记（使用搜索关键词获取token）
        for i, user_id in enumerate(TEST_USER_IDS[:2], 1):
            # 尝试使用搜索关键词获取xsec_token
            search_keyword = "美食"  # 可以根据实际情况调整
            results[f'get_user_notes_single_{i}'] = self.test_get_user_notes_single(
                user_id=user_id,
                limit=5,
                search_keyword=search_keyword if use_search_token else None
            )
        
        # 测试5: 获取多个用户笔记
        results['get_users_notes'] = self.test_get_users_notes(
            user_ids=TEST_USER_IDS,
            max_users=2,
            notes_per_user=3
        )
        
        # 测试6: 获取用户URL（如果API提供）
        if use_search_token:
            results['get_user_url'] = self.test_get_user_url_with_token(
                user_id=TEST_USER_IDS[0],
                search_keyword="美食"
            )
        
        # 测试总结
        self.print_section("测试总结")
        
        passed = sum(1 for r in results.values() 
                    if isinstance(r, dict) and r.get('success') or r is True)
        total = len([r for r in results.values() if isinstance(r, dict) or isinstance(r, bool)])
        
        print(f"总测试数: {total}")
        print(f"通过数: {passed}")
        print(f"失败数: {total - passed}")
        if total > 0:
            print(f"成功率: {passed/total*100:.1f}%")
        
        print("\n详细结果:")
        for test_name, result in results.items():
            if isinstance(result, dict):
                status = "✅" if result.get('success') else "❌"
                msg = result.get('msg', 'N/A')
                print(f"  {status} {test_name}: {msg}")
            else:
                status = "✅" if result else "❌"
                print(f"  {status} {test_name}")
        
        return results


if __name__ == "__main__":
    # 创建测试实例
    tester = LocalAPITester(base_url=API_BASE_URL)
    
    # 运行所有测试（使用搜索获取token）
    results = tester.run_all_tests(use_search_token=True)
    
    # 保存测试结果
    with open("test_local_api_results.json", "w", encoding="utf-8") as f:
        # 只保存关键信息，避免数据过大
        simplified_results = {}
        for key, value in results.items():
            if isinstance(value, dict):
                simplified_results[key] = {
                    "success": value.get('success'),
                    "msg": value.get('msg'),
                    "data_count": len(value.get('data', {}).get('notes', [])) if 'notes' in str(value.get('data', {})) else None
                }
            else:
                simplified_results[key] = value
        
        json.dump(simplified_results, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 70)
    print("  测试结果已保存到 test_local_api_results.json")
    print("=" * 70)