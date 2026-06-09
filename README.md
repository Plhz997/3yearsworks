# 单词伴学系统

一个在原有单词测评系统基础上扩展的英语伴学应用。系统保留词汇测评、错题本、测评记录、后台词库管理、单词上传、用户管理等原功能，并新增番茄专注舱、虚拟咖啡人、白噪音、咖啡豆商店、皮肤兑换和大模型英语任务匹配。

## 核心功能

### 词汇测评
- 支持小学、初中、高中学段词库。
- 支持基础测评、智能测评和 50 题标准测评。
- 题型包含看英文选中文、看中文选英文、单词拼写、认识判断。
- 自动保存测评记录，生成正确率和水平分析。
- 错词自动进入错题本，支持后续复习。

### 今日学习桌面
- 登录后首页展示今日计划、今日专注、错词提醒和咖啡人状态。
- 支持一键进入咖啡馆专注模式。
- 增加阅读理解、七选五、英语精听、影子跟读提醒入口。
- 保留原有开始测评、历史记录、错题本、管理后台入口。

### 单词番茄专注舱
- 支持选择词书/词组和专注任务。
- 单词任务包含新词学习、错词复习、单词测评、拼写训练。
- 综合英语任务包含阅读理解、七选五、英语精听、影子跟读。
- 支持 10 到 60 分钟专注时长、5 分钟休息阶段、白噪音播放。
- 专注过程中记录完成数量、正确率、学习时长。
- 结束后生成学习报告、推荐下一轮任务，并奖励咖啡豆和能量值。

### 大模型任务匹配
- 阅读理解、七选五、英语精听、影子跟读可接入 OpenAI 兼容接口。
- 用户可选择学习水平、主题偏好和薄弱点。
- 大模型生成文章/听力脚本、具体题目、选项、参考答案、解析和学习步骤。
- 未配置 API Key 或接口失败时，系统自动使用本地兜底任务，不影响原功能。

### 咖啡人陪伴系统
- 支持可拖动虚拟宠物，类似桌面小助手。
- 咖啡人会根据学习状态切换文案和动画：
  - `idle`：等待学习
  - `focus`：陪学中
  - `break`：休息中
  - `encourage`：错词较多时鼓励复习
  - `warning`：中断较多时提醒
  - `celebrate`：完成任务或连续专注时庆祝
  - `sleepy`：长期未学习时困倦等待

### 商店与装扮
- 完成番茄任务获得咖啡豆和能量值。
- 商店支持兑换宠物、头像框、壁纸、轻量任务券和界面皮肤。
- 皮肤包含经典紫藤风、可爱奶糖风、炫酷霓虹风、玩偶绒绒风。
- 首页支持一键换肤，在已拥有皮肤之间快速切换。

### 后台管理
- 管理员登录后台。
- 用户管理：查看、搜索、删除用户。
- 词库管理：新增、编辑、删除、批量删除单词。
- 单词上传：支持上传时选择学段，文件第三列也可覆盖学段。
- 测评记录与数据统计。

## 技术栈

### 后端
- Python 3.8+
- Flask
- Flask-SQLAlchemy
- Flask-JWT-Extended
- Flask-CORS
- python-dotenv
- SQLite

### 前端
- Vue 3
- Vue Router
- Axios
- Vite

## 项目结构

```text
.
├── backend/
│   ├── api/
│   │   ├── admin.py
│   │   ├── auth.py
│   │   ├── pomodoro.py
│   │   ├── test.py
│   │   ├── user.py
│   │   └── vocabulary.py
│   ├── app/
│   ├── config/
│   ├── models/
│   ├── utils/
│   │   ├── llm_task_matcher.py
│   │   ├── sample_data.py
│   │   └── test_algorithm.py
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── router/
│   │   ├── utils/
│   │   └── views/
│   ├── package.json
│   └── vite.config.js
├── .gitignore
└── README.md
```

## 快速开始

### 1. 启动后端

```bash
cd backend
pip install -r requirements.txt
python run.py
```

后端默认运行在：

```text
http://localhost:8081
```

首次启动会自动创建数据库表、管理员账号和示例词库数据。

### 2. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端默认运行在：

```text
http://localhost:5173
```

如果 5173 被占用，Vite 会自动切换到下一个可用端口。

### 3. 管理员账号

```text
用户名：admin
密码：admin123
```

## 大模型配置

大模型配置是可选项。建议在 `backend/.env` 中配置，`.env` 已被 `.gitignore` 忽略，不要把真实 Key 提交到仓库。

```env
LLM_API_KEY="你的 API Key"
LLM_API_BASE="https://api.openai.com/v1"
LLM_MODEL="gpt-4o-mini"
```

也可以在启动后端前使用环境变量：

```bash
export LLM_API_KEY="你的 API Key"
export LLM_API_BASE="https://api.openai.com/v1"
export LLM_MODEL="gpt-4o-mini"
python run.py
```

如果使用其他兼容 `/chat/completions` 的服务，修改 `LLM_API_BASE` 和 `LLM_MODEL` 即可。

## Render 部署

建议在 Render 上建两个服务：一个 Flask 后端 Web Service，一个 Vue 前端 Static Site。

### 1. 部署后端 Web Service

在 Render 新建 `Web Service`，连接 GitHub 仓库。

推荐配置：

```text
Root Directory: backend
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: python run.py
```

后端环境变量：

```env
LLM_API_KEY=你的 API Key
LLM_API_BASE=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
JWT_SECRET_KEY=部署环境里换一个长随机字符串
SECRET_KEY=部署环境里换一个长随机字符串
```

后端启动后，Render 会给你一个地址，例如：

```text
https://your-backend.onrender.com
```

前端需要使用它的 API 地址：

```text
https://your-backend.onrender.com/api
```

### 2. 部署前端 Static Site

在 Render 新建 `Static Site`，连接同一个 GitHub 仓库。

推荐配置：

```text
Root Directory: frontend
Build Command: npm install && npm run build
Publish Directory: dist
```

前端环境变量：

```env
VITE_API_BASE_URL=https://your-backend.onrender.com/api
```

把 `your-backend` 替换成你的 Render 后端服务真实域名。

### 3. 部署注意事项

- Render 免费服务冷启动较慢，第一次访问后端可能需要等待几十秒。
- 当前项目默认使用 SQLite，Render 免费 Web Service 的本地磁盘不适合长期保存生产数据；如果要正式长期使用，建议后续换成 Render PostgreSQL 或其他云数据库。
- 不要把 `backend/.env` 上传到仓库，Render 的环境变量在控制台配置即可。

## 常用 API

### 认证
- `POST /api/auth/register`：用户注册
- `POST /api/auth/login`：用户登录
- `GET /api/auth/profile`：用户信息
- `POST /api/auth/admin/login`：管理员登录

### 测评
- `POST /api/test/start`：基础测评
- `POST /api/test/start/smart`：智能测评
- `POST /api/test/start/standard`：50 题标准测评
- `POST /api/test/submit`：提交测评
- `GET /api/test/records`：测评记录
- `GET /api/test/record/{id}`：测评详情

### 用户
- `GET /api/user/stats`：用户统计
- `GET /api/user/wrong_words`：错题本
- `DELETE /api/user/wrong_words/{id}`：移除错词

### 词库
- `GET /api/vocab/search`：查询词库
- `POST /api/vocab/add`：新增单词
- `PUT /api/vocab/{id}`：更新单词
- `DELETE /api/vocab/{id}`：删除单词
- `POST /api/vocab/batch-delete`：批量删除单词
- `POST /api/vocab/upload`：批量上传单词

### 番茄伴学
- `GET /api/pomodoro/groups`：获取词组
- `POST /api/pomodoro/start`：开始单词番茄任务
- `POST /api/pomodoro/match-task`：大模型匹配阅读/听力/口语任务
- `POST /api/pomodoro/submit`：提交番茄报告

### 管理员
- `GET /api/admin/stats`：后台统计
- `GET /api/admin/users`：用户列表
- `DELETE /api/admin/users/{id}`：删除用户

## 注意事项

- `backend/.env`、`backend/vocabulary.db`、`frontend/dist`、`__pycache__` 不应提交到仓库。
- 前端 API 默认请求当前主机的 `8081` 端口，例如 `http://localhost:8081/api`。
- 没有大模型 Key 时，阅读、七选五、精听、跟读仍能使用本地兜底任务。
- 原有词汇测评和后台管理功能仍保留，番茄伴学是在其基础上新增的功能。

## License

MIT License
