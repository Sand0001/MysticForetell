"""
塔罗牌释义抓取脚本 (Playwright 版本)
该网站是 React SPA，内容由 JS 动态渲染，必须用真实浏览器才能拿到数据。
"""
import json
import asyncio
from playwright.async_api import async_playwright

BASE_URL = "https://tarotqa.com/zh-CN/gallery/card/"
SAVE_PATH = "engines/tarot_meanings.json"

# ========== 78 张牌的 slug 映射 ==========
MAJOR_ARCANA = {
    "愚者": "the-fool", "魔术师": "the-magician", "女祭司": "the-high-priestess",
    "女皇": "the-empress", "皇帝": "the-emperor", "教皇": "the-hierophant",
    "恋人": "the-lovers", "战车": "the-chariot", "力量": "strength",
    "隐士": "the-hermit", "命运之轮": "wheel-of-fortune", "正义": "justice",
    "倒吊人": "the-hanged-man", "死神": "death", "节制": "temperance",
    "恶魔": "the-devil", "塔": "the-tower", "星星": "the-star",
    "月亮": "the-moon", "太阳": "the-sun", "审判": "judgement", "世界": "the-world"
}

NUM_MAP = {
    "一": "ace", "二": "two", "三": "three", "四": "four", "五": "five",
    "六": "six", "七": "seven", "八": "eight", "九": "nine", "十": "ten",
    "侍从": "page", "骑士": "knight", "女王": "queen", "国王": "king"
}

SUIT_MAP = {
    "权杖": "wands", "圣杯": "cups", "宝剑": "swords", "星币": "pentacles"
}


def build_card_list():
    """构造所有 78 张牌的 {中文名: slug} 映射"""
    cards = dict(MAJOR_ARCANA)
    for cn_suit, en_suit in SUIT_MAP.items():
        for cn_num, en_num in NUM_MAP.items():
            cards[f"{cn_suit}{cn_num}"] = f"{en_num}-of-{en_suit}"
    return cards


async def scrape_one_card(page, cn_name, slug):
    """
    用 Playwright 访问单张牌的详情页，提取正位和逆位数据。
    DOM 结构参考 (来自用户提供的真实渲染后 HTML):
      - h1: 牌名
      - p.mb-6: 简介描述
      - h3 包含 "关键词" -> 紧跟 div 中的 span 列表
      - h3 包含 "正位含义" -> 紧跟的 p
      - h3 包含 "象征意义" -> 紧跟的 p
      - h3 包含 "原型" -> 紧跟的 p
      逆位需要点击"逆位"按钮后，DOM 会切换内容。
    """
    url = f"{BASE_URL}{slug}"
    result = {"slug": slug}

    try:
        await page.goto(url, wait_until="networkidle", timeout=30000)
        # 等待 h1 出现，说明页面已渲染完成
        await page.wait_for_selector("h1", timeout=15000)

        # ---------- 提取正位数据 ----------
        result["简介"] = await _extract_text(page, "p.mb-6")
        result["正位_关键词"] = await _extract_keywords(page)
        result["正位_含义"] = await _extract_section(page, "正位含义")
        result["象征意义"] = await _extract_section(page, "象征意义")
        result["原型"] = await _extract_section(page, "原型")

        # ---------- 点击逆位按钮，提取逆位数据 ----------
        reversed_btn = page.locator("button", has_text="逆位")
        if await reversed_btn.count() > 0:
            await reversed_btn.first.click()
            await page.wait_for_timeout(800)  # 等待内容切换动画
            result["逆位_关键词"] = await _extract_keywords(page)
            result["逆位_含义"] = await _extract_section(page, "逆位含义")

        print(f"✅ {cn_name}")
    except Exception as e:
        print(f"❌ {cn_name}: {e}")

    return cn_name, result


async def _extract_text(page, selector):
    """提取指定选择器的文本"""
    el = page.locator(selector).first
    if await el.count() > 0:
        return (await el.text_content()).strip()
    return ""


async def _extract_keywords(page):
    """提取关键词 h3 后面的 span 列表"""
    h3 = page.locator("h3", has_text="关键词")
    if await h3.count() == 0:
        return []
    # 关键词在 h3 的父容器的 div > span 里
    parent = h3.first.locator("..")
    spans = parent.locator("div span")
    count = await spans.count()
    keywords = []
    for i in range(count):
        text = (await spans.nth(i).text_content()).strip()
        if text:
            keywords.append(text)
    return keywords


async def _extract_section(page, section_name):
    """提取指定标题（如 '正位含义'）后面紧跟的 p 段落"""
    h3 = page.locator("h3", has_text=section_name)
    if await h3.count() == 0:
        return ""
    # 找到 h3 的父 div，再在其中找 p
    parent = h3.first.locator("..")
    p = parent.locator("p")
    if await p.count() > 0:
        return (await p.first.text_content()).strip()
    return ""


async def main():
    cards = build_card_list()
    all_data = {}

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="zh-CN",
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        )
        page = await context.new_page()

        for cn_name, slug in cards.items():
            cn_name_result, data = await scrape_one_card(page, cn_name, slug)
            all_data[cn_name_result] = data

        await browser.close()

    # 保存
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print(f"\n✨ 全部完成！共抓取 {len(all_data)} 张牌，数据已保存至 {SAVE_PATH}")


if __name__ == "__main__":
    print("🚀 启动 Playwright 浏览器，开始深度抓取塔罗释义...")
    asyncio.run(main())
