import scrapy

class jobItem(scrapy.Item):
    jobTitle = scrapy.Field()
    jobDetail = scrapy.Field()
    jobDescription = scrapy.Field()
    jobFunction = scrapy.Field()
    yearsOfExperience = scrapy.Field()
    qualification = scrapy.Field()
    company = scrapy.Field()
    careerLevel = scrapy.Field()
    companyOverview = scrapy.Field()
    postedDate = scrapy.Field()
    location = scrapy.Field()