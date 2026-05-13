#!/bin/bash

BASE_URL="https://cdn.tarotqa.com/images-optimized/tarot/"
SAVE_DIR="assets/cards/"
mkdir -p "$SAVE_DIR"

download() {
    cn=$1
    en=$2
    if [ ! -f "$SAVE_DIR$cn.webp" ]; then
        echo "Downloading $cn..."
        curl -s -o "$SAVE_DIR$cn.webp" "$BASE_URL$en.webp"
    fi
}

# Major Arcana
download "愚人" "The_Fool"
download "魔术师" "The_Magician"
download "女祭司" "The_High_Priestess"
download "女皇" "The_Empress"
download "皇帝" "The_Emperor"
download "教皇" "The_Hierophant"
download "恋人" "The_Lovers"
download "战车" "The_Chariot"
download "力量" "Strength"
download "隐士" "The_Hermit"
download "命运之轮" "Wheel_of_Fortune"
download "正义" "Justice"
download "吊人" "The_Hanged_Man"
download "死神" "Death"
download "节制" "Temperance"
download "恶魔" "The_Devil"
download "高塔" "The_Tower"
download "星星" "The_Star"
download "月亮" "The_Moon"
download "太阳" "The_Sun"
download "审判" "Judgement"
download "世界" "The_World"

# Minor Arcana Suits
suits=("权杖:Wands" "圣杯:Cups" "宝剑:Swords" "星币:Pentacles")
nums=("一:Ace" "二:Two" "三:Three" "四:Four" "五:Five" "六:Six" "七:Seven" "八:Eight" "九:Nine" "十:Ten" "侍从:Page" "骑士:Knight" "女王:Queen" "国王:King")

for s in "${suits[@]}"; do
    cn_suit="${s%%:*}"
    en_suit="${s#*:}"
    for n in "${nums[@]}"; do
        cn_num="${n%%:*}"
        en_num="${n#*:}"
        download "${cn_suit}${cn_num}" "${en_num}_of_${en_suit}"
    done
done

echo "Done!"
