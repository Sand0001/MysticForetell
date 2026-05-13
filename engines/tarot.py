import random
import os
import json

class TarotEngine:
    """
    塔罗牌核心引擎
    - 基础数据: TAROT_DATA (牌名 -> [正位含义, 逆位含义, 元素, 图像描述])
    - 深度数据: tarot_meanings.json (从 tarotqa.com 抓取的专业释义)
    """

    # ========== 深度释义数据 (从 JSON 文件加载) ==========
    _meanings_cache = None

    @classmethod
    def _load_meanings(cls):
        """懒加载深度释义数据，只读一次文件"""
        if cls._meanings_cache is None:
            meanings_path = os.path.join(os.path.dirname(__file__), "tarot_meanings.json")
            if os.path.exists(meanings_path):
                with open(meanings_path, 'r', encoding='utf-8') as f:
                    cls._meanings_cache = json.load(f)
            else:
                cls._meanings_cache = {}
        return cls._meanings_cache

    # ========== 基础牌库数据 [正位, 逆位, 元素, 图像描述] ==========
    TAROT_DATA = {
        # 大阿尔卡那 22 张
        "愚者": ["自由、冒险、初心", "鲁莽、逃避、盲目", "风", "年轻旅人站在悬崖边，手持白玫瑰，身旁有白狗相伴。"],
        "魔术师": ["创造、掌控、智慧", "野心、欺骗、能力不足", "风", "桌上摆放四元素法器，一手指天一手画地，头顶无限符号。"],
        "女祭司": ["神秘、直觉、内敛", "封闭、多疑、消极", "水", "端坐黑白石柱间，手持卷轴，脚踏月亮。"],
        "女皇": ["温柔、孕育、丰盛", "放纵、虚荣、匮乏", "土", "坐在自然宝座上，周围繁花似锦，手持权杖。"],
        "皇帝": ["权威、稳重、掌控", "专制、固执、软弱", "火", "坐在刻满羊头的石座上，穿盔甲持安卡权杖。"],
        "教皇": ["指引、传统、信仰", "束缚、盲从、刻板", "土", "穿华丽教袍坐两柱间，信徒跪拜，手持三重十字架。"],
        "恋人": ["爱恋、抉择、羁绊", "矛盾、分歧、疏离", "风", "天使拉斐尔空中祝福，下方亚当夏娃身后有智慧树和生命树。"],
        "战车": ["奋进、掌控、胜利", "急躁、失控、内耗", "火", "战士站在黑白狮身人面兽拉的战车上，星空华盖。"],
        "力量": ["勇气、包容、温柔", "懦弱、压抑、偏执", "火", "女性温和地合上狮子的嘴，头顶无限符号。"],
        "隐士": ["自省、孤独、智慧", "自闭、孤僻、逃避", "土", "老者立于雪山巅，手提六角星灯笼。"],
        "命运之轮": ["转机、机遇、轮回", "波折、停滞、困境", "火", "巨大轮盘周围有狮子、公牛、雄鹰和天使。"],
        "正义": ["公正、理性、抉择", "偏见、纠结、不公", "风", "坐在石柱间，一手持天平一手持宝剑。"],
        "倒吊人": ["牺牲、等待、释怀", "固执、纠结、徒劳", "水", "倒挂在十字木架上，头后有光环，神情安详。"],
        "死神": ["蜕变、结束、新生", "抗拒、沉沦、停滞", "水", "身披黑甲的死神骑白马，远处是重生的太阳。"],
        "节制": ["平衡、调和、自愈", "失衡、纠结、放纵", "火", "天使一脚水中一脚岸上，倾倒圣杯之水。"],
        "恶魔": ["欲望、束缚、执念", "解脱、觉醒、挣脱", "土", "半人半羊的潘神坐石台上，锁链松垮的一对男女。"],
        "塔": ["变故、破碎、冲击", "逃避、隐患、压抑", "火", "雷电击中塔尖，皇冠坠落，人从窗户跳下。"],
        "星星": ["希望、治愈、憧憬", "迷茫、焦虑、失望", "风", "赤裸少女倾倒生命之水，上方有八角巨星。"],
        "月亮": ["迷茫、幻想、不安", "猜忌、恐惧、假象", "水", "两座高塔间悬挂月亮，下方有狗、狼和龙虾。"],
        "太阳": ["光明、喜悦、顺利", "自负、浮躁、短暂", "火", "裸体孩童骑白马，背后是金色向日葵和太阳。"],
        "审判": ["觉醒、反思、救赎", "麻木、逃避、抗拒", "火", "天使在云端吹号角，棺木中人们欢呼新生。"],
        "世界": ["圆满、达成、完整", "缺憾、停滞、局限", "土", "舞者在桂冠花环中起舞，四角有四圣兽。"],
    }

    # 自动填充小阿卡纳
    for suit, element in [("权杖", "火"), ("圣杯", "水"), ("宝剑", "风"), ("星币", "土")]:
        for num in ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "侍从", "骑士", "女王", "国王"]:
            name = f"{suit}{num}"
            if name not in TAROT_DATA:
                TAROT_DATA[name] = ["基础含义", "逆位含义", element, f"{suit}组{num}，象征{element}元素。"]

    @classmethod
    def get_shuffled_deck(cls):
        """生成一个新的、随机打乱的牌堆（包含正逆位状态）"""
        deck = []
        names = list(cls.TAROT_DATA.keys())
        random.shuffle(names)
        for name in names:
            is_reverse = random.choice([True, False])
            deck.append({"name": name, "is_reverse": is_reverse})
        return deck

    @classmethod
    def get_card_detail(cls, name, is_reverse):
        """获取单张牌的完整数据，融合基础数据和深度释义"""
        # 1. 基础数据
        base = cls.TAROT_DATA.get(name, ["未知", "未知", "未知", "无"])
        pos_m, neg_m, element, img_desc = base
        status = "逆位" if is_reverse else "正位"

        detail = {
            "name": name,
            "status": status,
            "meaning": neg_m if is_reverse else pos_m,
            "element": element,
            "image_desc": img_desc,
            "deep_meaning": ""
        }

        # 2. 融合深度释义
        meanings = cls._load_meanings()
        deep = meanings.get(name, {})
        if deep:
            prefix = "逆位" if is_reverse else "正位"
            keywords = deep.get(f"{prefix}_关键词", [])
            interp = deep.get(f"{prefix}_含义", "")
            intro = deep.get("简介", "")
            symbols = deep.get("象征意义", "")
            archetype = deep.get("原型", "")

            detail["deep_meaning"] = (
                f"【简介】{intro}\n"
                f"【关键词】{', '.join(keywords)}\n"
                f"【{status}含义】{interp}\n"
                f"【象征意义】{symbols}\n"
                f"【原型】{archetype}"
            )

        return detail
