from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from twisted.internet import reactor, defer
from reputePost.spiders.scraper import ReputePost
from pathlib import Path
def delete_file():
    file_path_list = [Path("Link.csv"), Path("Data.csv")]
    for file in file_path_list:
        if file.exists():
            file.unlink()
            print(f"{file} deleted successfully.")
        else:
            print(f"{file} not found.")

def check_marketplace_login():
    login_check = ReputePost()
    return login_check.login_successful

@defer.inlineCallbacks
def crawl():
    runner = CrawlerRunner()
    
    print("🚀 Starting Spider 1")
    yield runner.crawl(ReputePost)
    print("✅ Spider 1 finished!")

    reactor.stop()

def main():
    configure_logging({"LOG_LEVEL": "INFO"})
    try:
        check_loging = check_marketplace_login()
    except:
        check_loging = False
    if check_loging == True:
        try:
            delete_file()
            configure_logging()
            crawl()
            reactor.run()
            print('Done scraping Repute Post ✅')
        except Exception as e:
            print(f'❌ Repute Post scraping failed: {str(e)}')
            raise
    else:
        print(f'❌ Repute Post login not successful check it out')

if __name__ == "__main__":
    main()
