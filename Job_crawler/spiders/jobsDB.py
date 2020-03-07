import scrapy


class Job(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()
    company = scrapy.Field()


class JobSpider(scrapy.Spider):
    name = "jobsDB"
    allowed_domains = ['hk.jobsdb.com']
    start_urls = ['https://hk.jobsdb.com/hk/en/job/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0'}
    limit = 100
    jobs = list()
    def check_keywords(self,keywords):
        for keyword in keywords:
            if not any(keyword.strip()): keywords.pop(keywords.index(keyword))
        return keywords
      
    def start_requests(self):
        urls = [
            'https://hk.jobsdb.com/hk/jobs/%s/1' % self.category
        ]
        self.keywords = self.check_keywords(self.keywords.split(","))
        print("Searching for keywords:", self.keywords)
        for url in urls:
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        # extract all job links
        all_links = response.xpath(
            '//a[contains(@href,"https://hk.jobsdb.com/hk/en/job/")]/@href').getall()
        # extract all job titles
        all_titles = response.xpath(
            '//a[contains(@href,"https://hk.jobsdb.com/hk/en/job/")]').css('div::text').getall()
        # extract companies
        all_companies = response.xpath(
            '//a[contains(@href,"hk/jobs/companies/")]/@href').getall()
        # locate next page
        next_page = response.xpath(
            '//a[contains(@href,"/hk/jobs/information-technology/")]/span[contains(text(),"Next")]/../@href').get()
        # iterate over links
        for link, title,company in zip(all_links, all_titles,all_companies):
            if self.keywords:
                yield scrapy.Request(link, headers=self.headers, callback=self.parse_keyword, cb_kwargs=dict(keyword_list=self.keywords))
            self.jobs.append(Job(title=title, link=link,company=response.urljoin(company)))
        print(next_page)

        if next_page is not None:
            next_page = response.urljoin(next_page)
            print(next_page)
            yield scrapy.Request(next_page, headers=self.headers, callback=self.parse)

    def parse_keyword(self, response, keyword_list):
        keyword_dict = dict.fromkeys(keyword_list)
        for keyword in keyword_list:
            phrase_list = response.xpath('//*[contains(text(),"' + keyword +
                                         '")]/descendant::text()[not(parent::script)]').getall()
            keyword_dict[keyword] = len(phrase_list)
        print(keyword_dict)
