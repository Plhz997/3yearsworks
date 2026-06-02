# 单词测评系统

一个面向学生英语词汇水平检测的单词测评系统，支持匿名用户和注册用户两种测评模式，具备基础测评、用户记录、后台管理、词库管理等功能。

## 功能特点

### 基础测评功能
- 支持按学段选择词库：小学、初中、高中
- 随机抽取单词进行测评
- 多种测评形式：看英文选中文、看中文选英文、单词拼写、判断是否认识
- 详细的测评结果分析

### 测评算法
- **基础算法**：按词频和学段难度加权抽题，连续答对/答错时动态调整难度
- **智能算法**：结合用户错题本，个性化出题，错题优先重测

### 用户功能
- 用户注册、登录、退出
- 保存历史测评记录
- 查看最近测评成绩、历史平均成绩
- 错题本功能，记录薄弱词汇

### 后台管理
- 管理员登录后台
- 用户管理：查看、搜索、删除用户
- 词库管理：增删改查单词，支持按学段分类
- 测评记录管理
- 数据统计分析

## 技术栈

### 后端
- Python 3.8+
- Flask 2.0+
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-CORS

### 前端
- Vue 3
- Element Plus
- ECharts
- Axios

### 数据库
- SQLite（开发环境）
- MySQL（生产环境）

## 项目结构

```
vocabulary-test-system/
├── backend/                 # 后端代码
│   ├── api/                 # API路由
│   │   ├── auth.py          # 认证相关API
│   │   ├── test.py          # 测评相关API
│   │   ├── vocabulary.py    # 词库管理API
│   │   ├── user.py          # 用户相关API
│   │   └── admin.py         # 管理员API
│   ├── app/                 # Flask应用初始化
│   ├── config/              # 配置文件
│   ├── models/              # 数据库模型
│   ├── utils/               # 工具函数
│   │   ├── test_algorithm.py # 测评算法
│   │   └── sample_data.py   # 示例数据
│   ├── requirements.txt     # 依赖列表
│   └── run.py               # 启动文件
├── frontend/                # 前端代码
│   ├── src/
│   │   ├── router/          # 路由配置
│   │   ├── utils/           # 工具函数
│   │   └── views/           # 页面组件
│   │       └── admin/       # 管理后台页面
│   └── index.html           # 入口HTML
├── .gitignore               # Git忽略文件
└── README.md                # 项目说明
```

## 快速开始

### 环境要求
- Python 3.8+
- 现代浏览器

### 安装依赖

```bash
# 进入后端目录
cd backend

# 安装Python依赖
pip install -r requirements.txt
```

### 启动服务

```bash
cd backend
python run.py
```

服务将在 `http://localhost:5000` 启动。

### 大模型任务匹配配置（可选）

番茄伴学中的阅读理解、七选五、英语精听、影子跟读支持接入 OpenAI 兼容的大模型接口。未配置 API Key 时，系统会自动使用本地任务清单，不影响原有单词测评、错词本和后台管理功能。

```bash
export LLM_API_KEY="你的API Key"
export LLM_API_BASE="https://api.openai.com/v1"
export LLM_MODEL="gpt-4o-mini"
```

如果使用其他兼容 `/chat/completions` 的服务，将 `LLM_API_BASE` 和 `LLM_MODEL` 改成对应平台配置即可。

### 启动前端

直接用浏览器打开 `frontend/index.html` 即可。

### 登录信息

**管理员账号**：
- 用户名：admin
- 密码：admin123

## API接口

### 认证接口
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/admin/login` - 管理员登录
- `GET /api/auth/profile` - 获取用户信息

### 测评接口
- `POST /api/test/start` - 开始测评（匿名）
- `POST /api/test/start/smart` - 开始智能测评（登录用户）
- `POST /api/test/submit` - 提交测评结果
- `GET /api/test/records` - 获取用户测评记录

### 词库接口
- `GET /api/vocab/list` - 获取单词列表
- `GET /api/vocab/search` - 搜索单词
- `POST /api/vocab/add` - 添加单词（管理员）
- `PUT /api/vocab/{id}` - 更新单词（管理员）
- `DELETE /api/vocab/{id}` - 删除单词（管理员）

### 用户接口
- `GET /api/user/wrong_words` - 获取错题本
- `GET /api/user/favorites` - 获取收藏
- `GET /api/user/stats` - 获取用户统计

### 管理员接口
- `GET /api/admin/users` - 获取用户列表
- `DELETE /api/admin/users/{id}` - 删除用户
- `GET /api/admin/stats` - 获取统计数据

## 测评算法说明

### 基础测评算法

1. **分层抽题策略**：根据目标学段，按权重从当前学段(50%)、低一年级(25%)、高一年级(25%)抽取单词
2. **动态难度调整**：连续答对3题提高难度，连续答错3题降低难度
3. **水平估算**：根据正确率和答题情况综合评估词汇水平

### 智能测评算法

1. **个性化出题**：30%题目来自用户错题本，70%为新题目
2. **掌握程度分类**：掌握(正确率≥90%)、模糊(70%-90%)、薄弱(40%-70%)、不会(<40%)
3. **自适应调整**：优先选择薄弱词汇进行测试

## 数据库设计

### 用户表 (users)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| username | VARCHAR(50) | 用户名 |
| password | VARCHAR(255) | 密码(加密) |
| email | VARCHAR(100) | 邮箱 |
| created_at | TIMESTAMP | 创建时间 |

### 单词表 (vocabulary)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| word | VARCHAR(100) | 英文单词 |
| meaning | TEXT | 中文释义 |
| phonetic | VARCHAR(50) | 音标 |
| example | TEXT | 例句 |
| level | INTEGER | 学段(1-3) |
| frequency | INTEGER | 词频等级 |
| difficulty | INTEGER | 难度等级 |

### 测评记录表 (test_records)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户ID |
| level | INTEGER | 测评难度 |
| total_count | INTEGER | 总题数 |
| correct_count | INTEGER | 正确数 |
| accuracy | FLOAT | 正确率 |
| estimated_level | INTEGER | 预估水平 |

## License

MIT License
