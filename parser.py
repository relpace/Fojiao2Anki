import base64
import json
import requests
import gzip
from io import BytesIO

def transform(name,qs,n,i):
    with open (f"{n}_{name}.txt", 'a', encoding='utf-8') as file:
        headers = "#separator:tab\n#html:true\n#deck column:1\n#tags column:7\n"
        file.write(headers)
        separator = "\t"
        n = len(qs)
        for i in range(n):
            options=[]
            answers=[]
            for o in range(len(qs[i]['o'])):
                options.append(remove_newlines(str(qs[i]['o'][o])))
            for a in range(len(qs[i]['a'])):
                answers.append(remove_newlines(str(qs[i]['a'][a])))
            difficulty = remove_newlines(str(qs[i]['d']))
            false = remove_newlines(qs[i]['f'])
            question = remove_newlines(qs[i]['s'])
            answer = ''
            for j in range(len(answers)):
                answer += str(ord(answers[j])-ord("A")+1)
            file.write(name+separator+f"{name}#"+str(i)+separator+question+":{{c1::}}"+separator+"||".join(options)+separator+"||".join(answer)+separator+"难度:"+difficulty+"；"+"易错项:"+false+separator+"\n")
        print("写入成功")
def download(url):
    response = requests.get(url)
    print(response.status_code)
    return response.content


def process_file(n, i):
    url = f"https://f.7-xk.com/shuati/qFile/{n}.{i}.q"
    file_data = download(url)
    bin_data = base64.b64encode(file_data).decode('utf-8')
    a = {'bin': bin_data, 'q_time': i}
    bin_data = base64.b64decode(a['bin'])
    
    with gzip.GzipFile(fileobj=BytesIO(bin_data[1:])) as gz:
        decompressed_data = gz.read()
    
    u = json.loads(decompressed_data.decode('utf-8'))
    qs = [dict(item, i=str(item['i']), o=[o for o in item['o'] if o]) for item in u]
    return qs

def remove_newlines(input_string: str) -> str:
    cleaned_string = input_string.replace('\n', '').replace('\r', '')
    return cleaned_string

while True:
    n = input('请输入题库id')
    i = "123"
    result = process_file(n, i)
    transform(input("请输入题库名称"),result,n,i)
