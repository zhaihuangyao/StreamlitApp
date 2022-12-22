import datetime
import math

import chardet
import pandas as pd
import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect

# <editor-fold desc="初始化网络链接，并且获取配置数据 将数据封装成df输出">
# 创建了一个连接实例（connection object）
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)  # 这是这设置证书
conn = connect(credentials=credentials)  # 真正的连接器


# 通过 SQL query 来获取数据
# 用st.cache 去保存这些数据并且设置每10分钟更新一次

@st.cache(ttl=900)
def run_query(query):
    _rows = conn.execute(query, headers=1)
    _rows = _rows.fetchall()
    return _rows


# 通过配置文件获取要链接的链接
sheet_url = "https://docs.google.com/spreadsheets/d/1olgXQ4PxpHpjTNypq2F1ttmFh1C4pvoReua5oNbVqy4/edit#gid=251802293"
rows = run_query(f'SELECT * FROM "{sheet_url}"')
config_data = pd.DataFrame(rows)
# </editor-fold>


# 开始正式的内容制作
# 进行数据预制
config_version = "2022_12_19"  # 先确定当前的配置版本，这个由工具内部写定。
config_data = config_data[config_data["version"] == config_version]


# 读取配置的通用函数
def read_config(_config_name, _config_data=config_data):
    _config_value = _config_data.loc[0, _config_name]
    return _config_value


# 手册生成函数
def doc_marker(_number_dict):
    with open("G001活动地图数值设计.md", "rb") as f:
        content = f.read()
        result = chardet.detect(content)
    with open("G001活动地图数值设计.md", encoding=result["encoding"]) as f:
        markdown_string = f.read()
        formatted_markdown_string = markdown_string.format(**_number_dict)
        st.markdown(formatted_markdown_string)
        st.download_button("下载本文档", formatted_markdown_string)


# 用来计算文档数值的函数,返回数值对照字典
def doc_number_calculate(_map_name, _my_name, _event_dur, _story_difficulty, _all_difficulty, _map_scale,
                         _maple_foam):
    daily_energy_gain = read_config("核心玩家每日体力")
    story_energy_cost = daily_energy_gain * _event_dur * _story_difficulty
    all_energy_cost = daily_energy_gain * _event_dur * _all_difficulty
    cake_tower_factor = read_config("蛋糕塔难度系数")
    base_res_recycle_cof = read_config("基础资源回收比率")
    event_res_recycle_cof = read_config("活动资源回收比率")

    energy_value = read_config("每体力价值")
    gold_value = read_config("每金币价值")

    story_income_rate = read_config("剧情收益率")
    all_income_rate = read_config("全通关收益率")
    story_income_energy_prop = read_config("剧情收益体力占比")
    story_income_gold_prop = read_config("剧情收益金币占比")
    story_income_item_prop = read_config("剧情收益道具占比")
    all_income_energy_prop = read_config("扩展玩法收益体力占比")
    all_income_item_prop = read_config("扩展玩法收益道具占比")



    # 制备数值
    rare_res_mult = _map_scale / read_config("标准地图规模") if _map_scale / read_config("标准地图规模") <= read_config(
        "最大矿藏倍率") else read_config("最大矿藏倍率")
    base_res_recycle_value = round(base_res_recycle_cof * all_energy_cost * energy_value)
    event_res_recycle_value = round(event_res_recycle_cof * all_energy_cost * energy_value)

    story_income = round(story_energy_cost * energy_value * story_income_rate)  # 剧情总收益价值
    all_income = all_energy_cost * energy_value * all_income_rate  # 全通关玩法总收益价值

    story_energy_reward = round((story_income * story_income_energy_prop) / energy_value)
    story_gold_reward = round((story_income * story_income_gold_prop) / gold_value)
    story_item_reward = round((story_income * story_income_item_prop))
    story_exp_reward = round(story_energy_cost * read_config("每体力经验值获取") + (
            base_res_recycle_value + event_res_recycle_value) * read_config("道具消耗经验值获取"))

    chest_gold = round(story_gold_reward * 0.65)
    quest_gold = round(story_gold_reward * 0.25)
    hide_gold = round(story_gold_reward * 0.1)

    chest_energy = round(story_energy_reward * 0.45)
    idle_energy = round(story_energy_reward * 0.15)
    tea_energy = round(story_energy_reward * 0.25)
    hide_energy = round(story_energy_reward * 0.15)

    chest_item = round(story_item_reward * 0.7)
    hide_item = round(story_item_reward * 0.3)

    all_energy_reward = round((all_income * all_income_energy_prop) / energy_value)
    all_item_reward = round(all_income * all_income_item_prop)

    upgrade_energy = all_energy_reward * 0.5
    score_energy = all_energy_reward * 0.5
    upgrade_item = all_item_reward * 0.5
    score_item = all_item_reward * 0.5

    score_reward_value = score_energy * energy_value + score_item # 临时参数

    _number_dict = {
        "地图名称": _map_name,
        "设计师名称": _my_name,
        "今日日期": datetime.date.today(),
        "剧情难度系数": _story_difficulty,
        "积分难度系数": _all_difficulty,
        "地图规模": _map_scale,
        "配置版本": config_version,
        "活动持续时间": _event_dur,
        "剧情体力消耗": story_energy_cost,
        "剧情钥匙回收": _event_dur * 1,
        "剧情第一部分钥匙消耗": round(_event_dur * 1 * 0.14),
        "剧情第二部分钥匙消耗": round(_event_dur * 1 * 0.28),
        "剧情第三部分钥匙消耗": round(_event_dur * 1 * 0.58),
        "积分体力消耗": all_energy_cost,
        "积分任务额外体力消耗": all_energy_cost - story_energy_cost,
        "积分钥匙回收": _event_dur * 1,
        "基础资源磨损": base_res_recycle_value,
        "活动道具磨损": event_res_recycle_value,
        "基础资源体力磨损": round(base_res_recycle_value / energy_value),
        "活动资源体力磨损": round(event_res_recycle_value / energy_value),
        "蛋糕塔第一层的累计难度": round(cake_tower_factor * all_energy_cost * 0),
        "蛋糕塔第二层的累计难度": round(cake_tower_factor * all_energy_cost * 3),
        "蛋糕塔第三层的累计难度": round(cake_tower_factor * all_energy_cost * 8),
        "蛋糕塔第四层的累计难度": round(cake_tower_factor * all_energy_cost * 21),
        "蛋糕塔第五层的累计难度": round(cake_tower_factor * all_energy_cost * 55),
        "蛋糕塔第六层的累计难度": round(cake_tower_factor * all_energy_cost * 100),
        "蛋糕塔第一层的修建难度": round(cake_tower_factor * all_energy_cost * 0),
        "蛋糕塔第二层的修建难度": round(cake_tower_factor * all_energy_cost * (3 - 0)),
        "蛋糕塔第三层的修建难度": round(cake_tower_factor * all_energy_cost * (8 - 3)),
        "蛋糕塔第四层的修建难度": round(cake_tower_factor * all_energy_cost * (21 - 8)),
        "蛋糕塔第五层的修建难度": round(cake_tower_factor * all_energy_cost * (55 - 21)),
        "蛋糕塔第六层的修建难度": round(cake_tower_factor * all_energy_cost * (100 - 55)),
        "枫糖块藏量": round(read_config("枫糖块资源系数") * rare_res_mult * (1 - _maple_foam * 1.48)),
        "石英藏量": round(read_config("石英资源系数") * rare_res_mult),
        "彩虹石藏量": round(read_config("彩虹石资源系数") * rare_res_mult),
        "蘑菇藏量": round(read_config("蘑菇资源系数") * rare_res_mult),
        "火焰石藏量": round(read_config("火焰石资源系数") * rare_res_mult * (1 - _maple_foam * 1.56)),
        "金矿藏量": round(read_config("金矿资源系数") * rare_res_mult),
        "枫糖浆泡藏量": round(read_config("枫糖块资源系数") * rare_res_mult * (_maple_foam * 1.48) + read_config(
            "火焰石资源系数") * rare_res_mult * (_maple_foam * 1.56)),
        "主线总奖励价值": story_income,
        "主线总体力奖励": story_energy_reward,
        "主线总金币奖励": story_gold_reward,
        "主线总道具奖励价值": story_item_reward,
        "主线总经验值奖励": story_exp_reward,
        "剧情任务金币": quest_gold,
        "剧情任务小型装饰品": math.floor(_event_dur / 2),
        "剧情任务大型装饰品": math.floor(_event_dur / 3),
        "剧情任务经验值": story_exp_reward * 0.6,
        "建造经验值": story_exp_reward * 0.4,
        "宝箱金币": chest_gold,
        "宝箱体力": chest_energy,
        "宝箱道具价值": chest_item,
        "小体力晶块数量": round(chest_energy * 0.35 / 5),
        "中体力晶块数量": round(chest_energy * 0.25 / 8),
        "大体力晶块数量": round(chest_energy * 0.4 / 17),
        "小金币堆数量": round(chest_gold*0.03/20),
        "中金币堆数量": round(chest_gold*0.07/40),
        "大金币堆数量": round(chest_gold*0.3/80),
        "金币宝箱数量": round(chest_gold*0.6/400),
        "地图商人宝箱数量": round(chest_item*0.5/3.3),
        "倒下的收集品宝箱数量": round(chest_item*0.5*0.6/2.34),
        "正着的收集品宝箱数量": round(chest_item*0.5*0.4/3.12),
        "小龙宝箱数量": round(_event_dur * 2 * 1.5 * 0.6),
        "大龙宝箱数量": round(_event_dur * 2 * 1.5 * 0.4 / 2),
        "茶壶体力": idle_energy,
        "树洞金币": hide_gold,
        "树洞体力": hide_energy,
        "树洞道具": hide_item,
        "体力茶体力": tea_energy,
        "小奖品难度": round(all_energy_cost / 3000 * 250),
        "高级奖品难度": round(all_energy_cost / 3000 * 500),
        "豪华奖品难度": round(all_energy_cost / 3000 * 1250),
        "非凡奖品难度": round(all_energy_cost / 3000 * 2000),
        "绝妙奖品难度": round(all_energy_cost / 3000 * 2500),
        "终极大奖难度": round(all_energy_cost / 3000 * 3000),
        "小奖品价值": round(score_reward_value * 25/1800),
        "高级奖品价值": round(score_reward_value * 50/1800),
        "豪华奖品价值": round(score_reward_value * 150/1800),
        "非凡奖品价值": round(score_reward_value * 225/1800),
        "绝妙奖品价值": round(score_reward_value * 450/1800),
        "终极大奖价值": round(score_reward_value * 900/1800) ,
        "一级蛋糕塔体力": round(upgrade_energy/(30+3*_event_dur)*0.1),
        "二级蛋糕塔体力": round(upgrade_energy/(30+3*_event_dur)*0.2),
        "三级蛋糕塔体力": round(upgrade_energy/(30+3*_event_dur)*0.4),
        "四级蛋糕塔体力": round(upgrade_energy/(30+3*_event_dur)*0.4),
        "五级蛋糕塔体力": round(upgrade_energy/(30+3*_event_dur)*0.75),
        "六级蛋糕塔体力": round(upgrade_energy/(30+3*_event_dur)*1),
        "四级蛋糕塔道具": round(upgrade_item/(30+3*_event_dur)*0.77),
        "五级蛋糕塔道具": round(upgrade_item/(30+3*_event_dur)*0.77),
        "六级蛋糕塔道具": round(upgrade_item/(30+3*_event_dur)*1),
        "体力水罐数量":  round(chest_energy / 10)
    }
    return _number_dict


# <editor-fold desc="main">
def main():
    st.title("G001活动数值设计工具")
    st.text(f"当前本工具所使用的配置版本是{config_version}")
    st.header("请输入活动参数")
    col1, col2 = st.columns(2)
    with col1:
        my_name = st.text_input("请输入你的名字👇")
        map_name = st.text_input("请输入活动名称👇")
        event_dur = st.slider("请选择您活动的开启天数", min_value=3, max_value=7, value=5, step=1)
    with col2:
        story_diff_advice = read_config("剧情难度建议")
        all_diff_advice = read_config("全通关难度建议")
        story_difficulty = st.slider(f"你的活动的剧情通关难度系数，{story_diff_advice}", min_value=0.5,
                                     max_value=2.0, value=0.8, step=0.1)
        all_difficulty = st.slider(f"你的活动的完全通关难度系数，{all_diff_advice}", min_value=1.0,
                                   max_value=3.5, value=1.3, step=0.1)
        map_scale = st.slider("您的地图总Block体力数量,这代表了你的地图规模", min_value=5000, max_value=100000,
                              value=40000, step=5000)
        maple_foam = st.slider("(可选，默认0)你的地图是否需要用一定比例的枫浆泡泡替换枫糖和火焰石", min_value=0.0,
                               max_value=0.6,
                               value=0.0, step=0.05)

    # 创建按钮和操作逻辑
    if st.button("生成活动数值"):
        # st.title(f"{map_name}数值设计-{my_name}-{datetime.date.today()}")
        number_dict = doc_number_calculate(map_name, my_name, event_dur, story_difficulty, all_difficulty, map_scale,
                                           maple_foam)
        doc_marker(number_dict)


# </editor-fold>


if __name__ == "__main__":
    main()
