# 필요한 라이브러리들을 불러옵니다.
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk
import pandas as pd

# 네이버 뉴스에서 검색어에 해당하는 뉴스 제목, 링크, 날짜를 크롤링하는 함수입니다.
def fetch_naver_news_titles(search_query, tree):
    # 네이버 뉴스 검색 URL을 생성합니다.
    url = f"https://search.naver.com/search.naver?where=news&sm=tab_jum&query={search_query}"

    # 해당 URL로 요청을 보냅니다.
    response = requests.get(url)

    # 응답이 성공적이지 않은 경우 메시지를 출력하고 함수를 종료합니다.
    if response.status_code != 200:
        print("Failed to get data")
        return

    # 응답에서 HTML을 추출합니다.
    html = response.text
    # BeautifulSoup 객체를 생성하여 HTML을 파싱합니다.
    soup = BeautifulSoup(html, 'html.parser')

    # 뉴스 제목, 링크, 날짜 정보를 담을 리스트입니다.
    news_list = soup.select(".list_news .news_area")
    results = []

    # 각 뉴스 항목을 순회하며 필요한 정보를 추출합니다.
    for news in news_list:
        title = news.select_one(".news_tit").get('title')
        link = news.select_one(".news_tit").get('href')
        article_response = requests.get(link)
        article_html = article_response.text
        article_soup = BeautifulSoup(article_html, 'html.parser')
        
        date_tag = article_soup.find('meta', {'property': 'article:published_time'})
        
        # 해당 메타 태그가 없으면 계속 진행한다.
        if date_tag:
            date_content = date_tag['content']
            date = date_content.split('T')[0]
        else:
            date = "날짜 정보 없음"

        # 결과 리스트에 추출한 정보를 추가합니다.
        results.append([title, link, date])
        # GUI의 트리뷰에 결과를 추가합니다.
        tree.insert("", "end", values=(title, link, date))

    # 결과를 DataFrame으로 변환한 후 CSV 파일로 저장합니다.
    df = pd.DataFrame(results, columns=['제목', '링크', '날짜'])
    df.to_csv(f"{search_query}_news.csv", index=False, encoding='utf-8-sig')

# 검색 버튼이 눌렸을 때 실행될 함수입니다.
def search():
    # 사용자가 입력한 검색어를 가져옵니다.
    search_query = search_entry.get()
    # 검색어를 사용하여 뉴스 정보를 크롤링합니다.
    fetch_naver_news_titles(search_query, tree)

# GUI를 생성하고 구성합니다.
window = tk.Tk()
window.title("Naver News Search")

frame = ttk.Frame(window, padding="5")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

search_entry = ttk.Entry(frame, width=40)
search_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))

search_button = ttk.Button(frame, text="Search", command=search)
search_button.grid(row=0, column=1)

tree = ttk.Treeview(window, columns=("제목", "링크", "날짜"), show='headings')
tree.heading("#1", text="제목")
tree.heading("#2", text="링크")
tree.heading("#3", text="날짜")

tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# 스크롤바 추가 부분
scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))

# GUI를 실행합니다.
window.mainloop()
