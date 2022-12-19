import streamlit as st
from google.oauth2 import service_account
from gsheetsdb import connect
import pandas as pd

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

@st.cache(ttl=600)
def run_query(query):
    _rows = conn.execute(query, headers=1)
    _rows = _rows.fetchall()
    return _rows


# 通过配置文件获取要链接的链接，所以这个换成别的也可以？ 嗯。可以，所以我给改了。
sheet_url = "https://docs.google.com/spreadsheets/d/1olgXQ4PxpHpjTNypq2F1ttmFh1C4pvoReua5oNbVqy4/edit#gid=1930907310"
rows = run_query(f'SELECT * FROM "{sheet_url}"')  # 这个有点神奇？是在字符串中间插入了变量？通过{}？ 但是所有数据的抓取需要SQL还是有点难受啊。

# Try it
for row in rows:
    st.write(f"{row.version} has a:{row.config1}")

df = pd.DataFrame(rows)
st.write(df)

st.write(df['config1'])
new_version_df = df[df["version"] == "2022_11_15"]
st.write(new_version_df)



