import json
from urllib import request as urlrequest
from urllib.error import URLError, HTTPError

from config.config import Config


TASK_LABELS = {
    'reading': '阅读理解',
    'cloze7': '七选五',
    'listening': '英语精听',
    'shadowing': '影子跟读'
}


def build_fallback_task(task_type, level='高中', topic='日常学习'):
    label = TASK_LABELS.get(task_type, '综合英语')
    fallback_steps = {
        'reading': [
            {'title': '快速扫读文章', 'detail': f'围绕“{topic}”完成一篇{level}难度阅读，先判断主题和作者态度。', 'tips': ['看首尾段', '圈主题词']},
            {'title': '完成主旨题', 'detail': '选择最能概括全文中心的选项，并写一句理由。', 'tips': ['排除局部细节', '关注观点']},
            {'title': '定位细节题', 'detail': '回到原文找数字、转折、因果和同义替换。', 'tips': ['标定位句', '检查替换']},
            {'title': '整理长难句', 'detail': '记录 1 句影响理解的长难句，用中文复述结构。', 'tips': ['找主干', '拆从句']}
        ],
        'cloze7': [
            {'title': '判断篇章结构', 'detail': f'围绕“{topic}”完成一组七选五，先判断总分、转折或时间线结构。', 'tips': ['看段首', '找连接词']},
            {'title': '标空前空后线索', 'detail': '圈出代词、同义复现、转折词和并列词。', 'tips': ['代词指代', '逻辑关系']},
            {'title': '先填确定项', 'detail': '优先处理线索最明确的空，减少干扰选项。', 'tips': ['先易后难', '排除干扰']},
            {'title': '通读检查连贯', 'detail': '把答案带回全文，检查上下文是否顺。', 'tips': ['语气一致', '逻辑闭环']}
        ],
        'listening': [
            {'title': '第一遍抓大意', 'detail': f'听一段关于“{topic}”的{level}材料，先判断场景、人物关系和态度。', 'tips': ['不暂停', '抓主题']},
            {'title': '逐句精听', 'detail': '每 5 到 8 秒暂停，写关键词或完整句。', 'tips': ['实词优先', '空缺留白']},
            {'title': '核对原文', 'detail': '对照文本修正弱读、连读和漏听。', 'tips': ['标漏听', '记连读']},
            {'title': '整理词块', 'detail': '记录 3 个可复用表达。', 'tips': ['短语优先', '下次复听']}
        ],
        'shadowing': [
            {'title': '选择跟读片段', 'detail': f'选择一段关于“{topic}”的{level}音频或台词，控制在 30 到 60 秒。', 'tips': ['短材料', '难度适中']},
            {'title': '标重音停顿', 'detail': '在文本上标出重读词、停顿和升降调。', 'tips': ['重读实词', '按意群停顿']},
            {'title': '逐句模仿', 'detail': '一句一句跟读，先追准确度，再追速度。', 'tips': ['嘴型打开', '尾音清楚']},
            {'title': '录音自检', 'detail': '录一遍自己的声音，检查重音、连读和节奏。', 'tips': ['只改一处', '完整收尾']}
        ]
    }
    fallback_materials = {
        'reading': {
            'passage': (
                f'Tomorrow our school will hold a small exhibition about {topic}. '
                'Students are asked to collect information, make posters, and explain their ideas in English. '
                'Some students think the task is difficult, but others believe it is a good chance to learn by doing. '
                'The English teacher suggests that every group should choose one clear point and use simple examples.'
            )
        },
        'cloze7': {
            'passage': (
                f'Many students want to improve their English through {topic}. [1] '
                'First, they need a clear goal before they start. [2] '
                'Second, reviewing mistakes is more useful than only doing new exercises. [3] '
                'Finally, a short daily plan can make learning easier to continue. [4]'
            )
        },
        'listening': {
            'script': (
                f'Hi, everyone. Today I want to talk about {topic}. '
                'When we learn English, a small plan is often better than a very big dream. '
                'You can listen to a short passage, write down key words, and repeat useful sentences. '
                'If you keep doing this, your listening will become clearer.'
            )
        },
        'shadowing': {
            'script': (
                f'I used to think English speaking was difficult. '
                f'Then I started practicing with short clips about {topic}. '
                'I listened first, marked the stress, and repeated sentence by sentence. '
                'After a few days, I could speak more naturally.'
            )
        }
    }
    fallback_questions = {
        'reading': [
            {
                'stem': 'What is the main purpose of the school exhibition?',
                'options': ['To practice English through a project', 'To choose a new English teacher', 'To sell posters to students', 'To cancel group work'],
                'answer': 'To practice English through a project',
                'explanation': '文章强调通过收集信息、做海报和英文讲解来学习。'
            },
            {
                'stem': 'What does the teacher suggest each group should do?',
                'options': ['Choose one clear point', 'Use only difficult words', 'Work without examples', 'Make the longest poster'],
                'answer': 'Choose one clear point',
                'explanation': '原文提到 choose one clear point and use simple examples。'
            }
        ],
        'cloze7': [
            {
                'stem': 'Choose the best sentence for [1].',
                'options': ['But effort without a plan may not work well.', 'This is why lunch is important.', 'Most students dislike weekends.', 'The library closes very early.'],
                'answer': 'But effort without a plan may not work well.',
                'explanation': '后文说 First, they need a clear goal，说明前面应引出“需要计划”。'
            },
            {
                'stem': 'Choose the best sentence for [3].',
                'options': ['Mistakes show what we need to practice.', 'Sports can make people stronger.', 'The weather changes quickly.', 'Posters should be colorful.'],
                'answer': 'Mistakes show what we need to practice.',
                'explanation': '该空前后都在讲复盘错误，所以应填错误的作用。'
            }
        ],
        'listening': [
            {
                'stem': 'According to the script, what is often better than a very big dream?',
                'options': ['A small plan', 'A long holiday', 'A difficult test', 'A new notebook'],
                'answer': 'A small plan',
                'explanation': '脚本第二句直接说明 a small plan is often better。'
            },
            {
                'stem': 'What should learners write down while listening?',
                'options': ['Key words', 'Phone numbers', 'Every Chinese meaning', 'Song names'],
                'answer': 'Key words',
                'explanation': '脚本提到 write down key words。'
            }
        ],
        'shadowing': [
            {
                'stem': 'What should you mark before repeating?',
                'options': ['Stress', 'Prices', 'Page numbers', 'Pictures'],
                'answer': 'Stress',
                'explanation': '脚本提到 marked the stress。'
            },
            {
                'stem': 'How does the speaker practice?',
                'options': ['Sentence by sentence', 'Only by reading silently', 'By skipping the audio', 'By translating every word first'],
                'answer': 'Sentence by sentence',
                'explanation': '脚本提到 repeated sentence by sentence。'
            }
        ]
    }
    return {
        'source': 'fallback',
        'title': f'{level}{label} · {topic}',
        'task_type': task_type,
        'level': level,
        'topic': topic,
        'material': fallback_materials.get(task_type, fallback_materials['reading']),
        'questions': fallback_questions.get(task_type, fallback_questions['reading']),
        'steps': fallback_steps.get(task_type, fallback_steps['reading'])
    }


def match_learning_task(task_type, level='高中', topic='日常学习', weakness='', count=5):
    if not Config.LLM_API_KEY:
        return build_fallback_task(task_type, level, topic)

    system_prompt = (
        '你是一个英语学习系统的智能任务匹配器。'
        '请只输出 JSON，不要输出 Markdown。'
        'JSON 字段必须包含 title, task_type, level, topic, material, questions, steps。'
        'questions 至少 3 题，每题包含 stem, options, answer, explanation。'
        'steps 每项包含 title, detail, tips，tips 是字符串数组。'
        '阅读理解和七选五需要 material 和 questions；精听和影子跟读需要 material.script。'
    )
    user_prompt = {
        'task_type': task_type,
        'task_name': TASK_LABELS.get(task_type, task_type),
        'level': level,
        'topic': topic,
        'weakness': weakness,
        'step_count': count,
        'requirements': [
            '内容适合中学生英语学习，不要太长',
            '题目和步骤要能放进 25 分钟番茄钟',
            '给出可操作步骤，不要泛泛而谈',
            '如果是听力或跟读，生成一段可朗读英文脚本'
        ]
    }
    payload = {
        'model': Config.LLM_MODEL,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': json.dumps(user_prompt, ensure_ascii=False)}
        ],
        'temperature': 0.7,
        'response_format': {'type': 'json_object'}
    }
    req = urlrequest.Request(
        f"{Config.LLM_API_BASE.rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {Config.LLM_API_KEY}',
            'Content-Type': 'application/json'
        },
        method='POST'
    )
    try:
      with urlrequest.urlopen(req, timeout=25) as response:
          raw = json.loads(response.read().decode('utf-8'))
          content = raw['choices'][0]['message']['content']
          matched = json.loads(content)
          matched['source'] = 'llm'
          matched.setdefault('task_type', task_type)
          matched.setdefault('level', level)
          matched.setdefault('topic', topic)
          matched.setdefault('steps', [])
          return matched
    except (HTTPError, URLError, KeyError, ValueError, TimeoutError) as exc:
        print(f'LLM task matching failed: {exc}')
        return build_fallback_task(task_type, level, topic)
