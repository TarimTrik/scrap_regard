import requests
import lxml
from bs4 import BeautifulSoup
import json
import os


url = 'https://www.regard.ru/catalog'

headers = {
    'Accept': 'application/json, text/plain, */*',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'
}

path_temp = 'scrap_regard/temp'
path_data = 'scrap_regard/data'

def get_catalog_href(url, headers, path_temp):
    '''
    Find all catalog(menu_list) url, and create file in to temp folder 
    '''

    respons = requests.get(url, headers=headers)

    with open(f'{path_temp}/index.html', 'w') as file:
        file.write(respons.text)

    with open(f'{path_temp}/index.html') as file:
        stp = file.read()

    menu_list_href = {}

    soup = BeautifulSoup(stp, 'lxml')
    find_url_tree = soup.find('div', id='lmenu').find('ul')


    for items in find_url_tree:
        a_href = 'https://www.regard.ru' + items.find('a').get('href')
        a_text = items.find('a').text
        
        a_text_rep = a_text.replace(' ','_')
        a_href_rep = a_href.replace('.htm', '')

        menu_list_href[a_text_rep] = a_href_rep
    
    with open(f'{path_temp}/all_href.json', 'w') as file:
        json.dump(menu_list_href, file, indent=4, ensure_ascii=False)




def get_links(headers, path_temp):
    '''
    Goes to the link from catalog(menu_list), on this page searches for pagination and products, 
    Saves the product name and link to it, and goes to the next page from pagination, when pagination is over goes to the next link in catalog(menu_list). 
    '''

    block_links = {}

    with open(f'{path_temp}/all_href.json') as file:
        menu_list_href = json.load(file)

    count_get_data = 0

        # цикл забирає з файлу з списком силок каталогу і пісдя закінчення переходить до слідуючого списку з каталогу  
    for items_text, items_href in menu_list_href.items():
        
        # збереження та відкриття тимчасових файлів
        if os.path.isfile(f'{path_temp}/{count_get_data}_index.html'):
            with open(f'{path_temp}/{count_get_data}_index.html') as file:
                stp = file.read()
        else:
            r = requests.get(url=items_href, headers=headers)
            print(f'[requests.text.url] >> {items_text} >> [STATUS] {r}')
            
            with open(f'{path_temp}/{count_get_data}_index.html', 'w') as file:
                file.write(r.text)
            print(f'create {count_get_data}_index.html')

        

        # створення обєкт супа блоків з обєктами
        soup = BeautifulSoup(stp, 'lxml')
        bloks_content = soup.find('div', id='hits', class_='container').find('div', class_='content')
        
        # робота з пагінацією
        try:
            pages_num = int(bloks_content.find('div', class_='pagination').find_all('a', recursive=False)[-1].text)
            for num_page in range(1,pages_num + 1):
                urll = f'{items_href}/page{num_page}'

                ro = requests.get(url=urll, headers=headers)
                soup = BeautifulSoup(ro.text, 'lxml')
                bloks_content = soup.find('div', id='hits', class_='container').find('div', class_='content')
                bloks = bloks_content.find_all('div', class_='block')

                    # збирає всі силки з всіх блоків продуктів на сторінці і добавляє в файл        
                for blok in bloks:
                    block_href = 'https://www.regard.ru' + blok.find('div', class_='aheader').find('a').get('href')
                    block_head = blok.find('div', class_='aheader').find('a').text
                    block_links[block_head] = block_href
        except:
            print("**[ERROR] Pagination not found")
            for blok in bloks:
                    block_href = 'https://www.regard.ru' + blok.find('div', class_='aheader').find('a').get('href')
                    block_head = blok.find('div', class_='aheader').find('a').text
                    block_links[block_head] = block_href
            

        count_get_data +=1
    
    with open(f'{path_data}/links_tovarov.json', 'w') as file:
        json.dump(block_links, file, ensure_ascii=False, indent=4)



def get_data_page(path_data, headers):
    '''
    docstring
    '''

    with open(f'{path_data}/links_tovarov.json')as file:
        tovar_links = json.load(file)

    data_list = {}
    
    for name, link in tovar_links.items():
        resp = requests.get(link, headers=headers)
        soup = BeautifulSoup(resp.text, 'lxml')

        tabs = soup.find('div', id='hits-long', class_='container').find('div', id='tabs')
        tabs_table = tabs.find('div', id='tabs-1').find('tbody').find_all('tr')

        for tds in tabs_table:
            tds_first_name = tds.find('td', class_='first').text
            tds_second_name =  tds.find('td')

    data_list[tds_first_name] = tds_second_name


    # треба зробити шоб стягувало з сторінки всі дані
    # але є нюанс на кожному каталозі є рієні дані 
    # але все в вигляді таблиць 

    


def main(path_data, path_temp):
    '''
    Checks for folders (folder name), if not, creates them.
    Launches all functions in the order of their operation.
    '''

    if not os.path.exists(path_data):
        os.mkdir(path_data)

    if not os.path.exists(path_temp):
        os.mkdir(path_temp)

    # get_catalog_href(url, headers, path_temp)
    # get_links(headers, path_temp)
    get_data_page(path_data, headers)

if __name__ == "__main__":
    main(path_data, path_temp)