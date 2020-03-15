from PyPDF4 import PdfFileReader
import requests, re, os, shutil, glob, json

class Grabber(object):
    def __init__(self):
        self.archived = []
        self.stage = []
        self.archive = os.getcwd()+"\\archive\\"
        self.index_dir = os.getcwd()+"\\index\\"

        self.stats= {
            'total_downloads': 0,
            'total_bytes_downloaded': 0,
            'total_deleted': 0,
        }

        self.used_links = {}

        self.get_stage()
    
    def get_stage(self):
        for self.file in glob.glob("*.pdf"):
            self.stage.append(self.file)
    
    def export_stats(self):
        self.stats_path = self.index_dir + "stats.json"
        self.loaded_stats = json.load(open(self.stats_path))
        for self.key in self.stats.keys():
            self.loaded_stats[self.key] += self.stats[self.key]
        
        json.dump(self.loaded_stats, self.stats_path)
        

    def extract_information(self, pdf_path, link):
        with open(pdf_path, 'rb') as f:
            pdf = PdfFileReader(f)
            information = pdf.getDocumentInfo()
            number_of_pages = pdf.getNumPages()
        
        try:
            readable1 = extract_date(information.getText("/CreationDate").split('-'))
            readable2 = extract_date(information.getText("/ModDate").split('-'))
        except:
            readable1 = None
            readable2 = None
        
        info = {
            "author": information.author,
            "creator": information.creator,
            "producer": information.producer,
            "subject": information.subject,
            "title": information.title,
            "creation_date": readable1,
            "modification_date": readable2,
            "number_of_pages": number_of_pages,
            "download_link": link
        }

        return pdf_path, info

    def extract_date(self, stamp):
        switch = ''
        try:
            front, back = stamp[0], stamp[1]; factor = int(re.findall("[1-9]", back)[0])
        except: 
            front = stamp[0]; factor = 0

        seconds = front[-2::]
        minutes = front[-4:-2]
        hours = int(front[-6:-4])-5+factor

        if hours >= 23: hours=(hours%12); switch = "AM"
        elif hours > 12: hours=(hours%12); switch = "PM"
        else: switch = "AM"

        raw_date = ''.join(re.findall('[0-9]', front[:-6]))

        time = f"{hours}:{minutes}:{seconds}"
        date = f"{raw_date[4:6]}/{raw_date[6:8]}/{raw_date[0:4]}"

        return f"{date} - {time} {switch}"

    def download(self, url):
        expected_name = url.split('/')[-1]
        req = requests.get(url)
        self.used_links[url] = req.status_code
        if req.status_code and req.url == url:
            with open(expected_name, 'wb+')as data:
                data.write(req.content)
            self.get_stage()
            if f"url_{req.status_code}" in self.stats.keys(): self.stats[f'url_{req.status_code}'] +=1
            else: self.stats[f"url_{req.status_code}"] = 1
            self.stats['total_downloads'] +=1
            self.stats['total_bytes_downloaded'] += os.stat(expected_name).st_size
        else:
            self.stats[f'url_{req.status_code}'] +=1
            print('bad status')
    
    def archive_stage(self):
        for self.pdf in self.stage:
            self.archive_pdf(self.pdf)
    
    def archive_pdf(self, pdf):
        self.i = 1
        self.path = self.archive+pdf
        while os.path.isfile(self.path):
            self.path = self.archive+str(self.i)+pdf
            self.i+=1
        shutil.move(pdf, self.path)
    
    def delete_pdf(self, pdf):
        try:
            os.remove(self.archive+pdf) 
            self.stats['total_deleted'] +=1
        except Exception as error:
            raise error

if __name__ == '__main__':
    url = "https://www.markey.senate.gov/imo/media/doc/2015-02-06_MarkeyReport-Tracking_Hacking_CarSecurity%202.pdf"
    a = Grabber()
    # a.download(url)
    # a.export_stats()
    path = 'I-am-Malala-PDF-book-by-Malala-GrowPK.com_.pdf'
    a, info = a.extract_information(path, url)
print(info)
