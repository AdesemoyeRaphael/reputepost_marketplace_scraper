import pycountry
import requests
import scrapy
from twocaptcha import TwoCaptcha
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import logging
load_dotenv()

class ReputePost(scrapy.Spider):
    name = "rep"
    start_urls = ['https://reputepost.com/buyer/marketplace/paginatedindex']
    custom_settings = {
        "LOG_LEVEL": "INFO",
        "FEEDS": {
            "Data.csv": {"format": "csv", "encoding": "utf8", "overwrite": False},
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cookies = []
        self.api_key = os.getenv("API_KEY")
        self.email = os.getenv("EMAIL")
        self.password = os.getenv("PASSWORD")
        self.sitekey = os.getenv("SITE_KEY")
        self.login_successful = False
        self.login()
        self.get_page_len()

    def start_requests(self):
        page_number = 1
        request_body_list = ['https://reputepost.com/buyer/marketplace']
        while page_number <= self.page_leng:
            request_body = {
                'search[PriceFrom]': '',
                'search[PriceTo]': '',
                'search[MonthlyTrafic]': '',
                'search[WebsiteCategoriesList]': '',
                'search[WebsiteCategories]': '',
                'search[MonthlyTraficTo]': '',
                'search[ServiceType]': '',
                'search[DAFrom]': '',
                'search[DATo]': '',
                'search[AhrefFrom]': '',
                'search[AhrefTo]': '',
                'search[SpamScoreFrom]': '',
                'search[SpamScoreTo]': '',
                'search[LinkType]': '',
                'search[WebsiteLanguage]': '',
                'search[IsOwner]': '',
                'search[Rating]': '',
                'search[IsIncludeExample]': '',
                'search[IsFeatured]': '',
                'search[TLDs][]': '',
                'search[pageNumber]': str(page_number),
                'pageNumber': str(page_number)
            }
            request_body_list.append(request_body)
            page_number+=1
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9,ca;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "X-Requested-With": "XMLHttpRequest"
        }
        for body in request_body_list:
            if body == 'https://reputepost.com/buyer/marketplace':
                yield scrapy.Request(
                    url=body,
                    cookies=self.cookies,
                    headers=headers,
                    callback=self.parse
                )
            else:
                yield scrapy.Request(
                    url=self.start_urls[0],
                    method="POST",
                    body=self.encode_form_data(body),
                    cookies=self.cookies,
                    headers=headers,
                    callback=self.parse
                )

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        domain_list = []
        domain_element = soup.select('td:nth-child(1) .fs-15')
        for element in domain_element:
            domain_list.append(element.text.strip())

        cate_list = []
        cate_element = soup.select('td:nth-child(2)')
        for element in cate_element:
            cate_list.append(element.text.strip().replace('\n', ', '))

        lang_list = []
        lang_element = soup.select('.fw-400~ .fs-15.fw-400')
        for element in lang_element:
            lang_list.append(element.text.strip().replace('\n', ', '))

        country_list = []
        country_element = soup.find_all('div', {'class': 'mt-2 col-md-2 website-country'})
        for element in country_element:
            country_list.append(self.get_country_name(element.get('data-website-country')))
        
        price1_list = []
        price1_element = soup.select('#home div')
        for element in price1_element:
            price1_list.append(element.text.strip().replace('$', ''))

        price2_list = []
        price2_element = soup.select('.col-md-2 .mt-1+ .fw-600')
        for element in price2_element:
            element_text = element.text.strip().replace('$', '')
            if element_text == 'N/A':
                element_text = ''
            price2_list.append(element_text)

        link_no_list = []
        link_type_list = []
        link_no_element = soup.select('td:nth-child(1) .fs-15+ .text-quick-silver')
        for element in link_no_element:
            element_text = element.text.strip()
            if 'Max' in element_text or 'links' in element_text:
                max_no = element_text.split('Max ')[-1].strip().split(' ')[0].strip()
                link_no_list.append(max_no)
                if 'dofollow' in element_text.lower():
                    link_type_list.append('DoFollow')
                elif 'nofollow' in element_text.lower():
                    link_type_list.append('NoFollow')
                if 'dofollow/nofollow' in element_text.lower():
                    link_type_list.append('DoFollow/Nofollow')
            else:
                link_type_list.append('')
                link_no_list.append('')
        
        for domain, cate, lang, country, price1, price2, link_no, link_type in zip(domain_list, cate_list, lang_list, country_list, price1_list, price2_list, link_no_list, link_type_list):
            yield {
                'domain': domain,
                'marketplace': 'reputepost.com',
                'price':price1,
                'secondPrice': price2,
                'currency': 'USD',
                'country': country,
                'language': lang,
                'category': cate,
                'Info': f"Type of link: {link_type} \nNumber of links: {link_no}",
            }
    
    def get_country_name(self, alpha2_code):
        if alpha2_code == '':
            return alpha2_code
        country = pycountry.countries.get(alpha_2=alpha2_code.upper())  # Ensure uppercase
        return country.name if country else None

    def encode_form_data(self, data):
        """Encodes form data in application/x-www-form-urlencoded format"""
        from urllib.parse import urlencode
        return urlencode(data)
    
    def solve_cloudfare_captcha(self):
        logging.info("Solving captcha")
        solver = TwoCaptcha(self.api_key)
        try:
            result = solver.turnstile(
                sitekey=self.sitekey,
                url="https://reputepost.com/account/login",
            )
            captcha_code = result.get("code") or result.get("request")
            logging.info("Successfully solved the captcha")
            return {"code": captcha_code, "Success": True}
        except Exception as e:
            logging.info("Error solving CAPTCHA:", e)
            return {"code": "", "Success": False}

    def login(self):
        logging.info("Attempting to login....")
        session = requests.Session()
        active = True
        retry_no = 0
        while active:
            if retry_no <= 10:
                retry_no +=1
                captcha_response = self.solve_cloudfare_captcha()
                if captcha_response['Success'] == True:
                    captcha_code = captcha_response['code']
                    active = False
                    break
                else:
                    logging.info('Trying to resolve capther again')
            else:
                logging.info('Max number of retries reached')
                break

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        request_response = session.get('https://reputepost.com/account/login', headers=headers)
        soup = BeautifulSoup(request_response.text, "html.parser")
        try:
            verification_token = soup.find("input", {"name": "__RequestVerificationToken"}).get("value")
        except AttributeError:
            logging.info("Failed to find CSRF tokens.")
            raise AttributeError
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://reputepost.com",
            "Referer": "https://reputepost.com/account/login",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        body = {
            "LoginDto.Email": self.email,
            "LoginDto.Password": self.password,
            "LoginDto.KeepLoggedIn": True,
            "LoginDto.TurnstileToken": captcha_code,
            "cf-turnstile-response": captcha_code,
            "__RequestVerificationToken": verification_token,
            "LoginDto.KeepLoggedIn": False
        }
        request_response_login = session.post('https://reputepost.com/account/login', data=body, headers=headers)
        logging.info(request_response_login.status_code)
        login_response_cookies = requests.utils.dict_from_cookiejar(session.cookies)
        if login_response_cookies.get('.AspNetCore.Identity.Application') != None:
            for k, v in login_response_cookies.items():
                self.cookies.append({'name': k, 'value': v})
            self.login_successful = True
            logging.info("Login Successful")
        else:
            logging.info("Login not successful")
    
    def get_page_len(self):
        cookies_str = self.format_cookies(self.cookies)
        url = 'https://reputepost.com/buyer/marketplace/paginatedindex'
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9,ca;q=0.8",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Cookie": cookies_str
        }
        body = {
            'search[PriceFrom]': '',
            'search[PriceTo]': '',
            'search[MonthlyTrafic]': '',
            'search[WebsiteCategoriesList]': '',
            'search[WebsiteCategories]': '',
            'search[MonthlyTraficTo]': '',
            'search[ServiceType]': '',
            'search[DAFrom]': '',
            'search[DATo]': '',
            'search[AhrefFrom]': '',
            'search[AhrefTo]': '',
            'search[SpamScoreFrom]': '',
            'search[SpamScoreTo]': '',
            'search[LinkType]': '',
            'search[WebsiteLanguage]': '',
            'search[IsOwner]': '',
            'search[Rating]': '',
            'search[IsIncludeExample]': '',
            'search[IsFeatured]': '',
            'search[TLDs][]': '',
            'search[pageNumber]': '1',
            'pageNumber': '1'
        }
        response = requests.post(url, data=body, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        self.page_leng = int(soup.select_one(".pageSize").text.strip())
        logging.info(f"Total number of page: {self.page_leng}")
    
    def format_cookies(self, cookies):
        return '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])


