import httpx
from config import SILICONFLOW_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_TEMPERATURE, LLM_TIMEOUT

# 各牌阵的牌位名称定义
SPREAD_POSITIONS = {
    "single": ["今日指引"],
    "three": ["过去", "现在", "未来"],
    "celtic": [
        "① 现状（核心处境）",
        "② 挑战（当前阻碍）",
        "③ 意识（理性认知）",
        "④ 潜意识（内心真实感受）",
        "⑤ 过去（影响现状的过往）",
        "⑥ 近未来（即将发生的趋势）",
        "⑦ 自我（问卜者的态度）",
        "⑧ 环境（外部影响）",
        "⑨ 希望与恐惧",
        "⑩ 最终结果"
    ]
}

class AIInterpreter:
    @staticmethod
    async def get_interpretation(cards, spread_type, user_context="", element_analysis=None):
        positions = SPREAD_POSITIONS.get(spread_type, ["牌位"])

        # 构造牌阵详细描述
        cards_detail = ""
        for i, card in enumerate(cards):
            pos_label = positions[i] if i < len(positions) else f"第{i+1}张"
            cards_detail += f"""
### {pos_label}: {card['name']} ({card['status']})
- 元素: {card['element']}
- 基础含义: {card['meaning']}
- 深度释义: {card.get('deep_meaning', '暂无')}
- 牌面图像: {card['image_desc']}
"""

        # 元素平衡分析
        analysis_str = ""
        if element_analysis:
            total = sum(element_analysis.values())
            analysis_str = "【元素能量分布】：" + "，".join(
                [f"{k}元素 {v}张({round(v/total*100)}%)" for k, v in element_analysis.items()]
            )

        # 根据牌阵类型调整解读要求
        if spread_type == "celtic":
            interpretation_guide = """逐张解读，每张牌的开头必须标注：「第X张：牌名（正/逆位）— 牌位含义」。
例如：「第一张：权杖十 正位 — 现状」

核心原则：每张牌的解读都必须紧扣来访者提出的问题。不要泛泛解读牌义，而要回答"这张牌针对 ta 的困惑说了什么"。
解读节奏：先用一两句话描述牌面画面，再用"你"把牌面意象与来访者的问题连接起来。
①②合讲（现状与挑战），③④对比（意识与潜意识），⑤回望过去，⑥展望近未来，⑦⑧对比（自我与环境），⑨点出深层恐惧或期待，⑩给出方向。
牌与牌之间串成围绕来访者问题的连贯故事。最后一两句话收束。"""
        elif spread_type == "three":
            interpretation_guide = """逐张解读，每张牌的开头必须标注：「第X张：牌名（正/逆位）— 牌位含义」。
例如：「第一张：圣杯八 逆位 — 过去」

核心原则：每张牌都必须紧扣来访者提出的具体问题来解读。不要脱离问题讲通用牌义，而要回答"这张牌针对 ta 的问题告诉我什么"。

解读节奏：先用一两句描述牌面画面，再用"你"把牌义与来访者的困惑连接。
- 过去那张牌：围绕问题，点出"在这件事上，过去留下了什么影响"。
- 现在这张牌：围绕问题，说清“你在这件事上当下的状态是什么”。
- 未来那张牌：围绕问题，给出"如果顺着当前的能量，这件事可能朝哪个方向发展"。
三张牌串成围绕来访者问题的"从哪来、在哪里、往哪去"故事。最后一两句收束。"""
        else:
            interpretation_guide = """开头标注：「牌名（正/逆位）— 今日指引」。

核心原则：解读必须紧扣来访者提出的具体问题。不要泛泛解释牌义，而要回答"这张牌针对 ta 的困惑说了什么"。
解读节奏：先用一两句描述牌面画面，再用"你"把牌面意象与来访者的问题连接起来，最后给出针对这个问题的方向感指引。一两句话收束。"""

        prompt = f"""你是陈默，一位沉稳温柔的塔罗占卜师。

来访者的困惑：「{user_context or "请给我近期的生活指引"}」
牌阵：{"单牌" if spread_type == "single" else "三牌阵" if spread_type == "three" else "凯尔特十字"}

抽到的牌：
{cards_detail}
{analysis_str}

{interpretation_guide}

【风格要求】
1. 最重要：所有解读必须紧紧围绕来访者提出的具体问题展开。每张牌都要回答"这张牌针对 ta 的问题说了什么"，而不是泛泛解释牌义。
2. 描述牌面时，是在说「这张牌上画着什么」。不要写成来访者面前真的有那些东西。描述画面和连接来访者处境之间的过渡要自然流畅，不要每张牌都用同一个句式。可以灵活运用各种方式，比如：
   - "牌上这个背着十根权杖的人，弯着腰却不肯放手——你是不是也正扛着不该属于你的重量？"
   - "圣杯中的水溢了出来。在感情这件事上，你可能给得太多了。"
   - "我看到一座高塔被闪电劈中——有些你以为稳固的东西，其实早就在松动了。"
   每张牌的表达方式要有变化，不要形成机械的套路。
3. 每张牌开头必须清晰标注牌名、正逆位和牌位含义。
4. 逆位不是坏牌，是转机信号。语气温柔直接，不故弄玄虚。
5. 禁止编造具体生活细节（金额、人名、具体事件）。不说"建议用Excel"之类。
6. 牌与牌串成连贯故事，不要孤立分析。结尾温暖有力。
7. 篇幅：单牌200字，三牌阵400字，凯尔特十字800字。言简意赅，不要啰嗦。
8. 纯文本输出，不用Markdown。段落间空行分隔。
"""

        payload = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": "你是陈默，二十年经验的塔罗占卜师。风格：先看牌面画面，再紧扣来访者的具体问题把牌义与处境连接，最后给出温暖指引。解读必须围绕来访者的问题展开，不要脱离问题泛泛而谈。不编造具体生活细节。说话直接、温柔、有力量。言简意赅。纯文本输出。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": LLM_TEMPERATURE
        }

        headers = {
            "Authorization": f"Bearer {SILICONFLOW_API_KEY}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(LLM_BASE_URL, json=payload, headers=headers, timeout=LLM_TIMEOUT)
            if response.status_code != 200:
                raise Exception(f"AI API Error: {response.text}")

            result = response.json()
            return result['choices'][0]['message']['content']
