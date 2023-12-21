import streamlit as st
import requests
import re
import pandas as pd
import altair as alt
from collections import Counter
from streamlit_echarts import st_pyecharts
import jieba
from pyecharts.charts import WordCloud as PyWordCloud
def crawl_webpage(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19042'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    response.encoding = 'utf-8'
    text_content = response.text
    pattern = r"[\u4E00-\u9FA5]+"
    matches = re.findall(pattern, text_content)
    filtered_words = [word for word in matches if len(word) > 1]
    words = jieba.cut(''.join(filtered_words))
    word_freq = Counter(words)
    word_freq = Counter({word: freq for word, freq in word_freq.items() if len(word) > 1})
    # print(word_freq)
    return word_freq


def generate_wordcloud(counts):
    words = list(counts.keys())
    word_counts = [(word, counts[word]) for word in words]
    wordcloud = PyWordCloud()
    wordcloud.add("", word_counts, word_size_range=[20, 100])
    st_pyecharts(wordcloud)

def main():
    st.title("静态网页爬虫")
    url = st.text_input("请输入网址：")
    with st.sidebar:
            chart_type= st.radio(
                "选择图表类型",
                ("饼图","条形图","折线图","回归图","直方图","词云","表格","动态线图")
            )
    if url:
        try:
            word_count = crawl_webpage(url)
            words = list(word_count.keys())
            counts = list(word_count.values())
            df = pd.DataFrame({'word': words, 'count': counts})
            df = df.nlargest(20, 'count')
            if chart_type == '饼图':
                chart = alt.Chart(df).mark_arc().encode(
                    color=alt.Color('word:N', scale=alt.Scale(scheme='category20b')),
                    angle='count',
                    tooltip=['word', 'count']
                ).properties(
                    width=600,
                    height=400,
                    title="页面关键字分布"
                )

            elif chart_type == '条形图':
                chart = alt.Chart(df).mark_bar().encode(
                    x='count:Q',
                    y=alt.Y('word:N', sort='-x'),
                    tooltip=['word', 'count']
                ).properties(
                    width=1200,
                    height=800,
                    title="页面关键字数量"
                )



            elif chart_type == '折线图':
                chart = alt.Chart(df).mark_line().encode(
                    x='word:N',
                    y='count:Q',
                    tooltip=['word', 'count']
                ).properties(
                    width=800,
                    height=600,
                    title="页面关键字趋势"
                )

            elif chart_type == '回归图':
                chart = alt.Chart(df).mark_circle().encode(
                    x='count',
                    y='word',
                    tooltip=['word', 'count']
                ).properties(
                    width=800,
                    height=600,
                    title='回归图'
                )

            elif chart_type == '直方图':
                chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X('count:Q', bin=True),
                    y='count()',
                    tooltip=['count()']
                ).properties(
                    width=800,
                    height=600,
                    title='直方图'
                )

            elif chart_type == '词云':
                generate_wordcloud(word_count)
                return

            elif chart_type == '表格':
                # 显示表格内容
                st.dataframe(df)
                return
            elif chart_type == '动态线图':
                # 添加动态线图
                st.line_chart(df['count'])
                return
            st.altair_chart(chart)

        except requests.exceptions.RequestException as e:
            st.error(f"发生错误：{e}")

if __name__ == "__main__":
    main()
