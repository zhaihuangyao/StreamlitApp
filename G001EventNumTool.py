import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect
import pandas as pd

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
def read_config(_config_data, _config_name):
    _config_value = _config_data.loc[0, _config_name]
    return _config_value


# 数据处理
story_diff_advice = read_config(config_data, "剧情难度建议")
score_diff_advice = read_config(config_data, "积分难度建议")


# <editor-fold desc="main">
def main():
    st.title("G001活动数值设计工具")
    st.text(f"当前本工具所使用的配置版本是{config_version}")
    config_data

    st.header("请输入活动参数")
    event_dur = st.slider("请选择您活动的开启天数", min_value=3, max_value=7, value=5, step=1)

    story_difficulty = st.slider(f"请选择您的活动期望的剧情通关难度系数，{story_diff_advice}", min_value=0.5,
                                 max_value=1.2, value=0.8)
    score_difficulty = st.slider(f"请选择您的活动期望的积分通关难度系数，{score_diff_advice}", min_value=1.0,
                                 max_value=1.5, value=1.3)
    map_scale = st.slider("请选择您的地图总Block体力数量", min_value=5000, max_value=100000, value=40000, step=5000)

    # 创建按钮和操作逻辑
    st.button("生成活动数值")


# </editor-fold>


if __name__ == "__main__":
    main()
