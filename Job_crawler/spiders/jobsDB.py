import scrapy
class Job(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()

class JobSpider(scrapy.Spider):
    name = "jobsDB"
    allowed_domains = ['webcache.googleusercontent.com']
    start_urls = ['https://webcache.googleusercontent.com/search?q=cache:https://hk.jobsdb.com/',
    'https://hk.jobsdb.com/hk/en/job/']
    def start_requests(self):
        urls = [
            'https://hk.jobsdb.com/hk/jobs/information-technology/1'
        ]
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        for url in urls:
            yield scrapy.Request(url=url,headers=headers, callback=self.parse)

    def parse(self, response):
        jobs = list()
        hxs = scrapy.Selector(response)
        # extract all job links
        all_links = hxs.xpath('//a[contains(@href,"https://hk.jobsdb.com/hk/en/job/")]')
        # extract all job titles
        all_titles = hxs.xpath('//a[contains(@href,"https://hk.jobsdb.com/hk/en/job/")]').css('div::text').extract()
        # iterate over links
        for link, title in zip(all_links,all_titles):
            jobs.append(Job(title = title, link = link.attrib['href']))
        print(jobs)