import requests  # 웹 페이지 요청 모듈
from bs4 import BeautifulSoup  # 웹 페이지 파싱 모듈
import tkinter as tk  # GUI 프레임워크
from tkinter import ttk, messagebox  # tkinter의 테마 위젯 및 메시지 박스
import pandas as pd  # 데이터 분석 라이브러리
import webbrowser  # 웹 브라우저를 열기 위한 모듈
import os

# 프로젝트 폴더 경로
project_path = os.path.dirname(os.path.abspath(__file__))

# 작업 디렉토리 설정
os.chdir(project_path)

def on_tree_item_double_click(event):  # 트리 아이템 더블 클릭 이벤트 핸들러
    item = tree.selection()[0]  # 선택된 항목의 ID를 가져옵니다.
    webbrowser.open(tree.item(item, "values")[1])  # 해당 항목의 링크를 웹 브라우저로 엽니다.

def fetch_naver_news_titles(search_query, tree):  # 네이버 뉴스 제목을 가져오는 함수
    tree.delete(*tree.get_children())  # 트리뷰의 모든 자식 항목을 삭제합니다.
    url = f"https://search.naver.com/search.naver?where=news&sm=tab_jum&query={search_query}"  # 검색 쿼리를 포함한 URL
    response = requests.get(url)  # 해당 URL의 웹 페이지를 가져옵니다.

    if response.status_code != 200:  # 요청이 실패했을 경우
        print("Failed to get data")
        return

    html = response.text  # 웹 페이지의 HTML을 가져옵니다.
    soup = BeautifulSoup(html, 'html.parser')  # BeautifulSoup 객체 생성

    news_list = soup.select(".list_news .news_area")  # 뉴스 목록 선택
    results = []

    for news in news_list:  # 각 뉴스 아이템을 순회
        try:
            title = news.select_one(".news_tit").get('title')  # 뉴스 제목
            link = news.select_one(".news_tit").get('href')  # 뉴스 링크
            article_response = requests.get(link)  # 뉴스 링크의 페이지를 가져옵니다.
            article_html = article_response.text  
            article_soup = BeautifulSoup(article_html, 'html.parser')
            
            date_tag = article_soup.find('meta', {'property': 'article:published_time'})  # 발행 시간 메타 태그
            date = date_tag['content'].split('T')[0] if date_tag else "날짜 정보 없음"  # 발행 날짜
            
            results.append([title, link, date])  # 결과 리스트에 추가
            tree.insert("", "end", values=(title, link, date))  # 트리뷰에 항목 추가
        except Exception as e:
            print(f"An error occurred while processing the news link {link}. Error: {e}")

    df = pd.DataFrame(results, columns=['제목', '링크', '날짜'])  # 결과를 데이터프레임으로 변환
    df.to_csv(f"{search_query}.csv", index=False, encoding='utf-8-sig') # 결과를 CSV 파일로 저장

def search():  # 검색 버튼 클릭 시 실행되는 함수
    search_query = search_entry.get()  # 검색 입력창의 텍스트를 가져옵니다.
    try:
        fetch_naver_news_titles(search_query, tree)  # 뉴스 제목 가져오기 함수 호출
        messagebox.showinfo("성공", "뉴스 검색이 완료되었습니다!")  # 성공 메시지 박스 표시
    except Exception as e:
        messagebox.showerror("오류", f"뉴스 검색 중 오류가 발생했습니다. 오류 메시지: {e}")  # 오류 메시지 박스 표시

window = tk.Tk()  # 메인 윈도우 객체 생성
window.title("Naver News Search")  # 윈도우 제목 설정
window.geometry("650x480")  # 윈도우 크기 설정

frame = ttk.Frame(window, padding="5")  # 프레임 객체 생성
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  # 프레임 그리드 배치

search_entry = ttk.Entry(frame, width=40)  # 검색 입력창 객체 생성
search_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))  # 입력창 그리드 배치

search_button = ttk.Button(frame, text="Search", command=search)  # 검색 버튼 객체 생성
search_button.grid(row=0, column=1)  # 버튼 그리드 배치

tree = ttk.Treeview(window, columns=("제목", "링크", "날짜"), show='headings', height=20)  # 트리뷰 객체 생성
tree.heading("#1", text="제목")  # 첫 번째 칼럼 제목 설정
tree.heading("#2", text="링크")  # 두 번째 칼럼 제목 설정
tree.heading("#3", text="날짜")  # 세 번째 칼럼 제목 설정

tree.column("#1", width=150)  # 첫 번째 칼럼 너비 설정
tree.column("#2", width=300)  # 두 번째 칼럼 너비 설정
tree.column("#3", width=150)  # 세 번째 칼럼 너비 설정

tree.bind("<Double-1>", on_tree_item_double_click)  # 더블 클릭 이벤트 바인딩

tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))  # 트리뷰 그리드 배치

scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)  # 스크롤바 객체 생성
tree.configure(yscrollcommand=scrollbar.set)  # 트리뷰에 스크롤바 설정
scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))  # 스크롤바 그리드 배치

window.mainloop()  # 메인 루프 실행
