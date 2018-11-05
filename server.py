import os
import requests
import socket
import time
from bs4 import BeautifulSoup


class ConsoleLogBase(object):
    ''' ConsoleLog '''
    PORT = 9000
    BASE_URL = 'https://team-aft.virtd.deere.com/job/aft_burnin_dev/'\
        '{BUILDNO}/consoleFull'

    def __init__(self):
        _buildNo = os.environ['BUILD_NUMBER']
        print _buildNo
        self.host = socket.gethostname()
        self.url = self.BASE_URL.format(BUILDNO=_buildNo)
        self.pageContent = self._get_page_content()
        self.soup = None
        self.initialize()

    def initialize(self):
        ''' initialize '''
        self.soup = self._initialize_soup()

    def _get_page_content(self):
        ''' _get_page_content '''
        res = requests.get(self.url)
        if res.status_code == 200:
            return res.content
        raise InvalidStatusCodeException(
            'Status code: %s for %s "INVALID"' % (res.status_code, self.url))
    
    def _initialize_soup(self):
        ''' _initialize_soup '''
        return BeautifulSoup(self.pageContent, 'html.parser')

    def _initialize_socket(self):
        ''' _initialize_socket '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.PORT))
        return sock

    def send_data_to_logstash(self):
        ''' send_data_to_logstash '''
        consoleDataList = self.soup.get_text()
        data = consoleDataList.split("\n")
        for line in data:
            try:
                sock = self._initialize_socket()
                sock.send(b'{LINE}'.format(LINE=line))
            except UnicodeEncodeError as e:
                print line, e
            finally:
                sock.close()

if __name__ == '__main__':
    c = ConsoleLogBase()
    c.send_data_to_logstash()