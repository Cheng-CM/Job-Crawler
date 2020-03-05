import scrapy


class Job(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()


class JobSpider(scrapy.Spider):
    name = "jobsDB"
    allowed_domains = ['hk.jobsdb.com']
    start_urls = ['https://hk.jobsdb.com/hk/en/job/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

    def start_requests(self):
        urls = [
            'https://hk.jobsdb.com/hk/jobs/information-technology/1'
        ]

        for url in urls:
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        jobs = list()
        test_keyword_list = ["Python", "Java", "AWS"]
        # extract all job links
        all_links = response.xpath(
            '//a[contains(@href,"https://hk.jobsdb.com/hk/en/job/")]/@href').getall()
        # extract all job titles
        all_titles = response.xpath(
            '//a[contains(@href,"https://hk.jobsdb.com/hk/en/job/")]').css('div::text').getall()
        # locate next page
        next_page = response.xpath(
            '//a[contains(@href,"/hk/jobs/information-technology/")]/span[contains(text(),"Next")]/../@href').get()
        # iterate over links
        for link, title in zip(all_links, all_titles):
            yield scrapy.Request(link, headers=self.headers, callback=self.parse_keyword,cb_kwargs=dict(keyword_list=test_keyword_list))
            jobs.append(Job(title=title, link=link))

        print(jobs)
        print(next_page)

        if next_page is not None:
            next_page = response.urljoin(next_page)
            print(next_page)
            yield scrapy.Request(next_page, headers=self.headers, callback=self.parse)

    def parse_keyword(self, response, keyword_list):
        for keyword in keyword_list:
            phrase_list = response.xpath('//*[contains(text(),"' + keyword +
                                         '")]/descendant::text()[not(parent::script)]').getall()
            print("Keyword: %s Appear %s Time(s)" % (keyword, len(phrase_list)))
