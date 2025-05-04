import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import os
import logging
import re

# 配置日志记录
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_html(url):
    """获取网页的HTML内容"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"获取URL {url} 时发生错误: {e}")
        return None

def convert_unix_timestamp_to_time(unix_timestamp):
    """将Unix时间戳转换为HH:mm格式"""
    try:
        date_time = datetime.utcfromtimestamp(int(unix_timestamp))
        formatted_time = date_time.strftime('%H:%M')
        return formatted_time
    except Exception as e:
        logging.error(f"转换时间戳 {unix_timestamp} 时出错: {e}")
        return ""

def extract_flight_details(html, search_string, url):
    """提取单个页面的所有航班信息"""
    soup = BeautifulSoup(html, 'html.parser')
    extracted_data = []
    
    try:
        # 找到所有航班行
        flight_rows = soup.find_all('tr', class_='data-row')
        logging.debug(f"找到 {len(flight_rows)} 个航班行")

        for i, row in enumerate(flight_rows, 1):
            try:
                # 尝试提取每一行的详细信息
                logging.debug(f"第 {i} 行航班信息:")
                
                # 提取日期
                try:
                    date_element = row.find('td', class_='hidden-xs hidden-sm', attrs={'data-time-format': 'DD MMM YYYY'})
                    if date_element:
                        logging.debug(f"日期: {date_element.text.strip()}")
                        date = date_element.text.strip()
                    else:
                        raise ValueError("日期元素未找到")
                except Exception as date_err:
                    logging.warning(f"无法提取日期: {date_err}")
                    continue
                
                # 提取FROM和TO
                try:
                    from_label = row.find('label', text=re.compile(r'FROM'))
                    to_label = row.find('label', text=re.compile(r'TO'))
                    
                    if from_label and to_label:
                        from_span = from_label.find_next_sibling('span', class_='details')
                        to_span = to_label.find_next_sibling('span', class_='details')
                        
                        if from_span and to_span:
                            fr = from_span.text.split('(')[0].strip()
                            to = to_span.text.split('(')[0].strip()
                            
                            logging.debug(f"出发地: {fr}, 目的地: {to}")
                        else:
                            raise ValueError("FROM或TO span元素未找到")
                    else:
                        raise ValueError("FROM或TO label元素未找到")
                except Exception as loc_err:
                    logging.warning(f"无法提取位置信息: {loc_err}")
                    continue
                
                # 检查是否包含搜索字符串
                if search_string.lower() in fr.lower() or search_string.lower() in to.lower():
                    # 提取预计起飞时间 (STD)
                    std = ""
                    try:
                        std_label = row.find('label', text=re.compile(r'STD'))
                        if std_label:
                            std_span = std_label.find_next_sibling('span', class_='details')
                            if std_span:
                                std_timestamp = std_span.get('data-timestamp')
                                std_offset = std_span.get('data-offset')
                                if std_timestamp and std_offset:
                                    std_adjusted_timestamp = int(std_timestamp) + int(std_offset)
                                    std = convert_unix_timestamp_to_time(std_adjusted_timestamp)
                                    logging.debug(f"预计起飞时间: {std}")
                                else:
                                    raise ValueError("STD时间戳或偏移量未找到")
                            else:
                                raise ValueError("STD span元素未找到")
                        else:
                            raise ValueError("STD label元素未找到")
                    except Exception as std_err:
                        logging.warning(f"无法提取预计起飞时间: {std_err}")
                    
                    # 提取预计到达时间 (STA)
                    sta = ""
                    try:
                        sta_label = row.find('label', text=re.compile(r'STA'))
                        if sta_label:
                            sta_span = sta_label.find_next_sibling('span', class_='details')
                            if sta_span:
                                sta_timestamp = sta_span.get('data-timestamp')
                                sta_offset = sta_span.get('data-offset')
                                if sta_timestamp and sta_offset:
                                    sta_adjusted_timestamp = int(sta_timestamp) + int(sta_offset)
                                    sta = convert_unix_timestamp_to_time(sta_adjusted_timestamp)
                                    logging.debug(f"预计到达时间: {sta}")
                                else:
                                    raise ValueError("STA时间戳或偏移量未找到")
                            else:
                                raise ValueError("STA span元素未找到")
                        else:
                            raise ValueError("STA label元素未找到")
                    except Exception as sta_err:
                        logging.warning(f"无法提取预计到达时间: {sta_err}")
                    
                    extracted_data.append({
                        'url': url,
                        'date': date,
                        'from': fr,
                        'to': to,
                        'std': std,
                        'sta': sta
                    })
            
            except Exception as row_err:
                logging.error(f"处理第 {i} 行时发生错误: {row_err}")

    except Exception as e:
        logging.error(f"提取航班信息时发生错误: {e}")
    
    return extracted_data

def main():
    # 定义要查询的URL列表
    urls = [
        "https://www.flightradar24.com/data/aircraft/b-5976",
        "https://www.flightradar24.com/data/aircraft/b-6507",
        "https://www.flightradar24.com/data/aircraft/b-6635",
        "https://www.flightradar24.com/data/aircraft/b-1316",
        "https://www.flightradar24.com/data/aircraft/b-1317",
        "https://www.flightradar24.com/data/aircraft/b-8119",
                
    ]
    
    search_string = "shenzhen"
    all_extracted_data = []

    for url in urls:
        try:
            # 获取网页HTML内容
            html = fetch_html(url)
            if not html:
                continue
            
            # 提取并打印当前页面的所有航班信息
            extracted_data = extract_flight_details(html, search_string, url)
            all_extracted_data.extend(extracted_data)

        except Exception as e:
            logging.error(f"抓取页面 {url} 时发生错误: {e}")
    
    # 处理CSV文件
    output_file = "output.csv"
    if os.path.exists(output_file):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_output_file = f"output_{timestamp}.csv"
        os.rename(output_file, new_output_file)
        logging.info(f"重命名现有文件为: {new_output_file}")

    # 将所有提取的数据写入新的CSV文件
    if all_extracted_data:
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['URL', 'Date', 'From', 'To', 'STD', 'STA'])
            for row_data in all_extracted_data:
                writer.writerow([row_data['url'], row_data['date'], row_data['from'], row_data['to'], row_data['std'], row_data['sta']])
                logging.info(f"写入数据: {row_data}")
    else:
        logging.info(f"No data containing '{search_string}' was found on any page.")

if __name__ == '__main__':
    main()



