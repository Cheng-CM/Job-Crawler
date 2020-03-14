import scrapy
import json
import urllib.parse as urlparse

class JobSpider(scrapy.Spider):
    name = "jobsDB"
    allowed_domains = ['hk.jobsdb.com', 'xapi.supercharge-srp.co']
    start_urls = ['https://hk.jobsdb.com/hk/en/job/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0'}
    API_headers = {
        "Host": "xapi.supercharge-srp.co",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0",
        "Accept": "*/*",
        "Accept-Language": "zh-TW,zh;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://hk.jobsdb.com/hk/industry/information-technology/1",
        "content-type": "application/json",
        "Origin": "https://hk.jobsdb.com",
        "Content-Length": "2234",
        "DNT": "1",
        "Connection": "keep-alive",
        "TE": "Trailers"
    }
    # Default Settings
    current = 0
    limit = 100
    category = "information-technology"
    # keywords = "Python"

    # def check_keywords(self, keywords):
    #     for keyword in keywords:
    #         if not any(keyword.strip()):
    #             keywords.pop(keywords.index(keyword))
    #     return keywords

    def start_requests(self):
        urls = [
            'https://hk.jobsdb.com/hk/jobs/%s/1' % self.category
        ]
        # self.keywords = self.check_keywords(self.keywords.split(","))
        # print("Searching for keywords:", self.keywords)
        for url in urls:
            yield scrapy.Request(url=url, headers=self.headers, callback=self.parse)

    def parse(self, response):
        # extract all job links
        all_links = response.xpath(
            '//a[contains(@href,"https://hk.jobsdb.com/hk/en/job/")]/@href').getall()
        # extract all job titles
        # self.jobs["title"] = response.xpath(
        #     '//a[contains(@href,"https://hk.jobsdb.com/hk/en/job/")]').css('div::text').getall()
        # # extract companies
        # self.jobs["company"] = response.xpath(
        #     '//a[contains(@href,"hk/jobs/companies/")]/@href').getall()
        # locate next page
        next_page = response.xpath(
            '//a[contains(@href,"/hk/jobs/%s/")]/span[contains(text(),"Next")]/../@href' % self.category).get()
        # iterate over links

        for link in all_links:
            parsed = urlparse.urlparse(link)
            API_body = {
                "query": "{\n    jobDetail(jobId: \"" + urlparse.parse_qs(parsed.query)['jobId'][0] + "\",country: \"hk\",locale: \"en\") {\n      id\n      pageUrl\n      jobTitleSlug\n      applyUrls {\n       mobile\n       external\n       loggedInApply\n      }\n      isExpired\n      isConfidential\n      isClassified\n      accountNum\n      advertisementId\n      subAccount\n      showMoreJobs\n      adType\n      header {\n        banner {\n          bannerUrls {\n            large\n          }\n        }\n        salary {\n          max\n          min\n          type\n          extraInfo\n          currency\n          isVisible\n          salaryOnDisplay\n        }\n        logoUrls {\n          small\n          medium\n          large\n          normal\n        }\n        jobTitle\n        company {\n          name\n          url\n        }\n        review {\n          rating\n          numberOfReviewer\n        }\n        expiration\n        postedDate\n        isInternship\n      }\n      companyDetail {\n        companyWebsite\n        companySnapshot {\n          avgProcessTime\n          registrationNo\n          employmentAgencyPersonnelNumber\n          employmentAgencyNumber\n          telephoneNumber\n          workingHours\n          website\n          facebook\n          size\n          dressCode\n          nearbyLocations\n        }\n        companyOverview {\n          html\n        }\n        videoUrl\n        companyPhotos {\n          caption\n          url\n        }\n      }\n      jobDetail {\n        summary,\n        jobDescription {\n          html\n        },\n        jobRequirement {\n          careerLevel\n          yearsOfExperience\n          qualification\n          fieldOfStudy\n          industryValue {\n            value,\n            label\n          }\n          skills\n          employmentType\n          languages\n          postedDate\n          closingDate\n          jobFunctionValue {\n            code,\n            name,\n            children {\n              code,\n              name\n            }\n          },\n          benefits\n        },\n        whyJoinUs\n      },\n      location {\n        location\n        locationId\n        omnitureLocationId\n      }\n      sourceCountry\n    }\n  }"
            }
            yield scrapy.Request("https://xapi.supercharge-srp.co/job-details/graphql?country=hk", headers=self.API_headers, body=json.dumps(API_body), method="POST", callback=self.get_job_by_API)

        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, headers=self.headers, callback=self.parse)

    # def parse_keyword(self, response, keyword_list):
    #     keyword_dict = dict.fromkeys(keyword_list)
    #     for keyword in keyword_list:
    #         phrase_list = response.xpath('//*[contains(text(),"' + keyword +
    #                                      '")]/descendant::text()[not(parent::script)]').getall()
    #         keyword_dict[keyword] = len(phrase_list)
    #     print(keyword_dict)
    #     self.jobs["keywords"] += keyword_dict

    def get_job_by_API(self, response):
        self.current += 1
        data = json.loads(response.text)
        jobDetail = data["data"]["jobDetail"]
        print(jobDetail)