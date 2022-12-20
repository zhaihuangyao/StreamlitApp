import datetime

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
def doc_number_calculate(_map_name, _my_name, _event_dur, _story_difficulty, _score_difficulty, _map_scale):
    daily_energy_gain = read_config("核心玩家每日体力")
    story_energy_cost = daily_energy_gain * _event_dur * _story_difficulty
    score_energy_cost = daily_energy_gain * _event_dur * _score_difficulty
    cake_tower_factor = read_config("蛋糕塔难度系数")
    base_res_recycle_cof = read_config("基础资源回收系数")
    event_res_recycle_cof = read_config("活动资源回收系数")

    _number_dict = {
        "地图名称": _map_name,
        "设计师名称": _my_name,
        "今日日期": datetime.date.today(),
        "剧情难度系数": _story_difficulty,
        "积分难度系数": _score_difficulty,
        "地图规模": _map_scale,
        "配置版本": config_version,
        "活动持续时间": _event_dur,
        "剧情体力消耗": story_energy_cost,
        "剧情钥匙回收": _event_dur * 1,
        "剧情第一部分钥匙消耗": round(_event_dur * 1 * 0.14),
        "剧情第二部分钥匙消耗": round(_event_dur * 1 * 0.28),
        "剧情第三部分钥匙消耗": round(_event_dur * 1 * 0.58),
        "积分体力消耗": score_energy_cost,
        "积分任务额外体力消耗": score_energy_cost - story_energy_cost,
        "积分钥匙回收": _event_dur * 1,
        "基础资源体力磨损": base_res_recycle_cof * _score_difficulty * _event_dur,
        "活动道具体力磨损": event_res_recycle_cof * _score_difficulty * _event_dur,
        "蛋糕塔第一层的修建难度": cake_tower_factor * score_energy_cost * 0,
        "蛋糕塔第二层的修建难度": cake_tower_factor * score_energy_cost * 3,
        "蛋糕塔第三层的修建难度": cake_tower_factor * score_energy_cost * 8,
        "蛋糕塔第四层的修建难度": cake_tower_factor * score_energy_cost * 21,
        "蛋糕塔第五层的修建难度": cake_tower_factor * score_energy_cost * 55,
        "蛋糕塔第六层的修建难度": cake_tower_factor * score_energy_cost * 100
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
    with col2:
        event_dur = st.slider("请选择您活动的开启天数", min_value=3, max_value=7, value=5, step=1)
        story_diff_advice = read_config("剧情难度建议")
        score_diff_advice = read_config("积分难度建议")
        story_difficulty = st.slider(f"你的活动的剧情通关难度系数，{story_diff_advice}", min_value=0.5,
                                     max_value=1.2, value=0.8)
        score_difficulty = st.slider(f"你的活动的积分通关难度系数，{score_diff_advice}", min_value=1.0,
                                     max_value=1.5, value=1.3)
        map_scale = st.slider("您的地图总Block体力数量,这代表了你的地图规模", min_value=5000, max_value=100000,
                              value=40000, step=5000)

    # 创建按钮和操作逻辑
    if st.button("生成活动数值"):
        # st.title(f"{map_name}数值设计-{my_name}-{datetime.date.today()}")
        number_dict = doc_number_calculate(map_name, my_name, event_dur, story_difficulty, score_difficulty, map_scale)
        doc_marker(number_dict)


# </editor-fold>


if __name__ == "__main__":
    main()
