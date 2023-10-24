from icrawler.builtin import GoogleImageCrawler

crawler = GoogleImageCrawler(storage={'root_dir': r'C:\Users\мвм\Desktop\my_code\hack_perm\google_gun'})

count = 1000
name = 'люди с оружием в здании'

crawler.crawl(keyword=name, max_num=count)


