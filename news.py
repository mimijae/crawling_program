import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import webbrowser

def on_tree_item_double_click(event):
    item = tree.selection()[0]
    webbrowser.open(tree.item(item, "values")[1])

def fetch_naver_news_titles(search_query, tree):
    url = f"https://search.naver.com/search.naver?where=news&sm=tab_jum&query={search_query}"
    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to get data")
        return

    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    news_list = soup.select(".list_news .news_area")
    results = []

    for news in news_list:
        try:
            title = news.select_one(".news_tit").get('title')
            link = news.select_one(".news_tit").get('href')
            article_response = requests.get(link)
            article_html = article_response.text
            article_soup = BeautifulSoup(article_html, 'html.parser')
            
            date_tag = article_soup.find('meta', {'property': 'article:published_time'})
            
            date = date_tag['content'].split('T')[0] if date_tag else "날짜 정보 없음"
            
            results.append([title, link, date])
            tree.insert("", "end", values=(title, link, date))
        except Exception as e:
            print(f"An error occurred while processing the news link {link}. Error: {e}")

    df = pd.DataFrame(results, columns=['제목', '링크', '날짜'])
    df.to_csv(f"{search_query}_news.csv", index=False, encoding='utf-8-sig')

def search():
    search_query = search_entry.get()
    try:
        fetch_naver_news_titles(search_query, tree)
        messagebox.showinfo("성공", "뉴스 검색이 완료되었습니다!")
    except Exception as e:
        messagebox.showerror("오류", f"뉴스 검색 중 오류가 발생했습니다. 오류 메시지: {e}")

window = tk.Tk()
window.title("Naver News Search")
window.geometry("650x480")  # GUI 크기 조정

frame = ttk.Frame(window, padding="5")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

search_entry = ttk.Entry(frame, width=40)
search_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))

search_button = ttk.Button(frame, text="Search", command=search)
search_button.grid(row=0, column=1)

tree = ttk.Treeview(window, columns=("제목", "링크", "날짜"), show='headings', height=20)  # 트리뷰 크기 조정
tree.heading("#1", text="제목")
tree.heading("#2", text="링크")
tree.heading("#3", text="날짜")

tree.column("#1", width=150)  
tree.column("#2", width=300)  
tree.column("#3", width=150)  

tree.bind("<Double-1>", on_tree_item_double_click) 

tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

scrollbar = ttk.Scrollbar(window, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))

window.mainloop()
