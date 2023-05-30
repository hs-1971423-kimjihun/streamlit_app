from bs4 import BeautifulSoup
#from selenium import webdriver
import streamlit as st
import requests
import json
import re

#선언
a = [] # 가격용 리스트
b = [] # 이미지용 리스트
price= [] # 도구
data_list = []

keyward = st.text_input('키워드를 입력하세요.')
if st.button('검색 시작'):

    # 사용자가 키워드를 입력하면 해당 키워드로 URL 접속
    url = f"https://web.joongna.com/search/{keyward}"
    url2 = f"https://www.daangn.com/search/{keyward}/"  # 검색어에 따른 링크 저장

    st.write(f'크롤링 중: {url}')
    st.write(f'크롤링 중: {url2}')

    # HTTP GET 요청을 보내고 응답 받기
    response = requests.get(url)
    response2 = requests.get(url2)

    #st.write(f' {response.content}')

    # BeautifulSoup을 사용하여 HTML 파싱
    soup = BeautifulSoup(response.text, 'html.parser')
    soup2 = BeautifulSoup(response2.text, 'html.parser')
    #st.write(f'{soup2}')
    tab1, tab2, tab3 = st.tabs(['당근마켓', '중고나라', '종합'])



##
    with tab1:
        articles = soup2.find_all('article', class_='flea-market-article flat-card')

        for article in articles:
            img_src = article.find('div', class_='card-photo').img['src']
            article_title = article.find('span', class_='article-title').text
            article_price = article.find('p', class_='article-price').text

            st.image(img_src)
            st.write('제품 이름:', article_title)
            st.write('가격: ', article_price)
            st.write('---')

    with tab2:
        # tab B를 누르면 표시될 내용
        script_tag = soup.find("script", {"id": "__NEXT_DATA__"})

        if script_tag:
            # 태그 안의 텍스트 추출
            script_text = script_tag.string

            # JSON 데이터 파싱
            data = json.loads(script_text)
            items = data['props']['pageProps']['initialSearchItems']['items']
            #st.write(f'{items}')

            # 각 아이템에서 price, title, url 정보 추출 및 출력

            for item in items:
                price = item['price']
                title = item['title']
                url = item['url']
                st.image(url)
                st.write(f"Price: {price}\nTitle: {title}\n")
                st.write('---')
        else:
            print("해당 태그를 찾을 수 없습니다.")

    with tab3:
        #tab1의 price와 tab2의 price를 비교하여 평균, 최저값, 최대값을 구한다
        #평균값은 text로 출력하고, 최대값, 최저값은 해당하는 url, title도 같이 출력한다
        # tab1의 가격과 tab2의 가격을 비교하여 평균, 최저값, 최대값을 구합니다.
        col1, col2 = st.columns([1,1])
        # tab1의 price 추출
        tab1_prices = []
        articles = soup2.find_all('article', class_='flea-market-article flat-card')
        for article in articles:
            article_price = article.find('p', class_='article-price').text
            cleaned_price = re.sub(r'[^0-9,]', '', article_price)
            price = int(cleaned_price.replace(',', ''))
            tab1_prices.append(price)
            #st.write(f"tab1_price에 값{price}가 들어갔다.")

        #st.write(tab1_prices)

        # tab2의 price 추출
        tab2_prices = []
        script_tag = soup.find("script", {"id": "__NEXT_DATA__"})
        if script_tag:
            script_text = script_tag.string
            data = json.loads(script_text)
            items = data['props']['pageProps']['initialSearchItems']['items']
            for item in items:
                price = item['price']
                tab2_prices.append(price)

        #st.write(tab2_prices)

        # 최대값, 최소값, 평균값 계산 및 출력

        max_price = max(tab1_prices + tab2_prices)
        min_price = min(tab1_prices + tab2_prices)
        average_price = (sum(tab1_prices) + sum(tab2_prices)) / (len(tab1_prices) + len(tab2_prices))


        # 최대값과 최소값에 해당하는 URL과 제목 출력
        max_item = next(item for item in items if item['price'] == max_price)
        min_item = next(item for item in items if item['price'] == min_price)

        with col1:
            st.markdown('### 최대값 제품')
            st.text('모든 검색결과중 최대값으로 검색된 결과 입니다.')
            st.image(max_item['url'])
            st.write('최대값: ', max_price)
            st.write('제품이름: ', max_item['title'])

        with col2:
            st.markdown('### 최저값 제품')
            st.text('모든 검색결과중 최저값으로 검색된 결과 입니다.')
            st.image(min_item['url'])
            st.write('최소값:', min_price)
            st.write('제품이름: ', min_item['title'])

        st.info(f'평균값: {int(average_price)}')
