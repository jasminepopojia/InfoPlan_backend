# InfoPlan-致力于解决信息过载问题的App

一个基于小红书数据爬取和AI大模型的学习规划生成系统，支持用户搜索、笔记获取和智能学习路径规划。

## 📋 项目简介

本项目包含两个核心服务：

1. **爬虫服务（Spider Service）**：提供小红书用户、笔记等数据的爬取API
2. **模型服务（Model Service）**：基于AI大模型生成个性化学习规划

## ✨ 主要功能

### 爬虫服务功能
- 🔍 **用户搜索**：支持关键词搜索用户，支持分页和批量获取
- 📝 **笔记获取**：获取用户笔记、笔记详情、评论等
- 💾 **数据存储**：支持保存笔记数据到Excel、下载媒体文件
- 🌐 **API服务**：提供RESTful API接口，支持跨域访问

### 模型服务功能
- 🤖 **智能规划**：基于用户目标和笔记内容生成学习步骤
- 📚 **内容匹配**：自动匹配相关笔记到学习步骤
- 🎯 **个性化推荐**：根据用户ID列表获取相关笔记并生成规划

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js (用于执行JS加密脚本)
- 小红书Cookie（需要登录获取）

### 安装依赖

# 安装Python依赖
```
pip install -r requirements.txt
```

# 安装Node.js依赖（如果需要）
```
npm install
```

### 配置环境变量

创建 `.env` 文件：
```
COOKIES=your_xiaohongshu_cookies_here
```

### 启动爬虫服务

# 启动API服务（默认端口5001）

python api_server.py服务启动后，访问 `http://localhost:5001/health` 检查服务状态。

### 启动模型服务

# 设置环境变量
```
export SPIDER_API_URL=http://localhost:5001

export MODEL_PATH=/path/to/your/model 

export MODEL_SERVICE_PORT=5002
```

# 启动模型服务
```
cd XHS_Learing_Agent
python model_service_server.py
```

## 📖 API文档

### 爬虫服务API（端口5001）

#### 1. 搜索用户
```
POST /api/search/user
Content-Type: application/json

{
  "query": "美食",
  "page": 1,
  "proxies": {}  // 可选
}
```

**响应示例：**
```
{
  "success": true,
  "msg": "成功",
  "data": {
    "users": [...],
    "has_more": true
  }
}
```

#### 2. 批量搜索用户
```
POST /api/search/user/batch
Content-Type: application/json

{
  "query": "美食",
  "require_num": 15
}
```

#### 3. 获取用户笔记
```
POST /api/users/notes
Content-Type: application/json

{
  "user_ids": ["user_id1", "user_id2"],
  "max_users": 5,
  "notes_per_user": 5
}
```
#### 4. 获取单个用户笔记

```
GET /api/user/notes/{user_id}?limit=20
```

#### 5. 健康检查

```
GET /health
```

### 模型服务API（端口5002）

#### 生成学习规划
```
POST /api/learning/plan
Content-Type: application/json
{
  "goal": "我想学习AI agent的简单开发",
  "user_ids": ["user_id1", "user_id2"],
  "max_users": 5,
  "notes_per_user": 5,
  "debug": false
}
```

**响应示例：**
```
{
  "success": true,
  "msg": "学习规划生成成功",
  "data": {
    "goal": "我想学习AI agent的简单开发",
    "steps": [
      {
        "step_number": 1,
        "description": "了解AI Agent基础概念",
        "recommended_notes": [...]
      }
    ],
    "statistics": {
      "total_users": 5,
      "total_notes": 25,
      "total_steps": 5
    }
  }
}
```

## 🔧 使用示例

### Python代码示例

# 搜索用户

```
response = requests.post('http://localhost:5001/api/search/user', json={
    'query': '美食',
    'page': 1
})
users = response.json()
```

# 获取用户笔记
```
response = requests.post('http://localhost:5001/api/users/notes', json={
    'user_ids': ['user_id1', 'user_id2'],
    'max_users': 5,
    'notes_per_user': 5
})
notes = response.json()
```

# 生成学习规划
```
response = requests.post('http://localhost:5002/api/learning/plan', json={
    'goal': '我想学习Python爬虫',
    'user_ids': ['user_id1', 'user_id2'],
    'max_users': 5,
    'notes_per_user': 5
})
plan = response.json()
```

### 爬虫服务配置

在 `api_server.py` 中配置：
- 端口：默认5001
- Cookie：通过环境变量 `COOKIES` 设置

### 模型服务配置

在 `XHS_Learing_Agent/config.py` 中配置：
- `MODEL_PATH`: 模型文件路径
- `SPIDER_API_URL`: 爬虫服务地址
- `MODEL_SERVICE_PORT`: 模型服务端口

## 🔒 注意事项

1. **Cookie安全**：请妥善保管Cookie，不要提交到代码仓库
2. **请求频率**：请合理控制请求频率，避免被封禁
3. **数据使用**：请遵守小红书的使用条款，仅用于学习研究
4. **模型路径**：确保模型文件路径正确，模型服务才能正常启动

## 🛠️ 开发指南

### 添加新的API接口

1. 在 `apis/xhs_pc_apis.py` 中添加新的方法
2. 在 `api_server.py` 中添加对应的路由
3. 更新API文档

### 扩展数据提供者

1. 实现 `data_providers/interfaces.py` 中的接口
2. 在 `model_service` 中使用新的数据提供者

## 📄 许可证

本项目仅供学习研究使用，请勿用于商业用途。

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📮 联系方式

如有问题，请提交Issue或联系项目维护者。

---

**⚠️ 免责声明**：本项目仅用于技术学习和研究，使用者需自行承担使用风险，并遵守相关法律法规和平台规则。
