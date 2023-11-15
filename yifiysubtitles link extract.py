import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import threading

def extract_links(page, base_url, result_list, lock):
    url = f"{base_url}/language/english/page-{page}"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        ul_tag = soup.find('ul', {'class': 'media-list', 'itemtype': 'http://schema.org/Movie'})
        if ul_tag:
            links = ul_tag.find_all('a', href=True)
            link_strings = [f'"{base_url}{link["href"]}",' for link in links]
            with lock:
                result_list.extend(link_strings)
        else:
            print(f"Error: Unable to find the specified <ul> tag on page {page}.")
    else:
        print(f"Error: Unable to fetch the content from {url}")

def worker(start_page, end_page, base_url, result_list, lock, pbar):
    for page in range(start_page, end_page + 1):
        extract_links(page, base_url, result_list, lock)
        pbar.update(1)

def get_links(base_url, start_page, end_page, output_file, num_threads=5):
    total_links = 0
    unique_links = set()
    link_strings = []
    lock = threading.Lock()

    with tqdm(total=end_page - start_page + 1, desc="Pages") as pbar:
        threads = []
        result_list = []

        for _ in range(num_threads):
            thread = threading.Thread(target=worker, args=(start_page, end_page, base_url, result_list, lock, pbar))
            thread.start()
            threads.append(thread)
            start_page += (end_page - start_page + 1) // num_threads

        for thread in threads:
            thread.join()

        for link in result_list:
            full_link = link.strip()
            if full_link not in unique_links:
                total_links += 1
                unique_links.add(full_link)
                link_strings.append(full_link)

    # Save the links to the output file
    with open(output_file, 'w') as file:
        file.write('\n'.join(link_strings))

    print(f"Total unique links extracted: {total_links}")
    print(f"Links saved to {output_file}")

# Specify the base URL of the site
base_url = "https://yifysubtitles.ch"

# Specify the range of pages (1 to 2000)
start_page = 1
end_page = 2206

# Specify the output file
output_file = "yifidfdsaf.txt"

# Specify the number of threads to use
num_threads = 100

# Call the function to get and save all the unique href links within the specified <ul> tag using threading
get_links(base_url, start_page, end_page, output_file, num_threads)
