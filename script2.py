import pandas as pd
from gpt4free import forefront
prompt_head = '''I have the following [social association types]:
[c_assoc_type_id] 	[c_assoc_type_desc_chn]

0101	社會關係（籠統）
0102	同為……之成員
0103	社會交際
0202	師生關係
0203	學術交往
0204	學術主題相近
0205	同為……之成員
0206	學術襄助
0207	文學藝術交往
0208	學術攻訐
0301	朋友關係（籠統）
0401	政治關係（籠統）
0402	官場關係（平級）
0403	官場關係（下屬）
0404	官場關係（上司）
0405	政治奧援
0406	薦舉保任
0407	政治對抗
0501	著述關係（籠統）
0502	記詠文字
0503	墓誌文字
0504	序跋文字
0505	禮儀文字
0506	傳記文字
0507	論說文字
0508	箴銘文字
0509	書札文字
0510	應酬文字
0601	軍事關係（籠統）
0602	軍事支持
0603	軍事對抗
0701	醫療關係（籠統）
0801	宗教關係（籠統）
0901	家庭關係（籠統）
1001	財務關係（籠統）

I will provide you with the biographies of individuals from the Song dynasty. 
For each of the biography, they contain at least two names: [a], [b], [c], [d], etc.

After you read a biography of [a], please tell me the social association code(s) between [a] and others, namely between [a] and [b]; [a] and [c]; [a] and [d]; etc. Don't use any knowledge outside of the biography provided. The information that you need to capture to identify the social association but will be very close to the persons' name.

In addition, the relationship between two people might fall into multiple categories. For instance, they might have a 師生關係, as well as a 官場關係. Thus, please provide all the ones that apply; please also and rank them (more important ones first). 

You will also have to put your [reasoning] for choosing these associations types, and judging whether they are positive or negative. Use English when possible; be concise.

The output scheme should be a table like this:

|[task no] | [person 1] | [person 2] | [assoc_code] | [assoc_chn] | [positive/negative relationship] | [reasoning] |
| -- | -- | -- | -- | -- | -- | -- |
| task_number | [a] | [b] | c_assoc_type_id_1; c_assoc_type_id_2; etc. | c_assoc_type_desc_chn_1; c_assoc_type_desc_chn_2; etc. | positive/negative | reason |
| task_number | [a] | [c] | c_assoc_type_id_1; c_assoc_type_id_2; etc. | c_assoc_type_desc_chn_1; c_assoc_type_desc_chn_2; etc. | positive/negative | reason |

Before you work on the task, I will provide you with two examples that help you understand.

For task_number 900001, the biography of 徐几 is “徐几，字字与，号进斋，崇安人。博通经史，尤精于易。景定间与何基同以布衣召补迪功郎，添差建宁府教授，兼建安书院山长，撰经义以训式多士。” The biography mentions two people, [a] 徐几 and [b] 何基. The assoc_code for the relationship between 徐几 and 何基 is 0402; it is a positive relationship. 
For task_number 900002, the biography of 丁希亮 is “丁希亮，(1156～1192)，字少詹，黄巖人，世雄堂弟。从叶适学，又从陈亮、吕祖谦游。名言奥义，贯穿殆尽。论事深眇，皆有方幅。有丁少詹集(按县志著梅巖文集数十卷)。卒于绍熙三年，年四十七(按墓志作绍兴三年卒，以叶适生平推考之，应是绍熙之误)。” The biography mentions [a] 丁希亮, [b] 叶适, [c] 陈亮, [d] 吕祖. The relationship between 丁希亮 and 叶适 is 0202; 0203; 0206; positive.  The relationship between 丁希亮 and 陈亮 is 0203; 0206. The relationship between 丁希亮 and 吕祖 is 0207; 0301; positive.

If you understand, then work on these biographies.

'''

import time
import gpt4free
from gpt4free import Provider, quora, forefront
import os
start_time = time.time()
folder_path = './download_result/'
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
result = []

number_of_inputs = 4
df1 = pd.read_csv('song.csv')
df1 = df1[df1['name_number'] >= 2]
paragraphs = df1.values.tolist()

for i in range(1000, 4000, number_of_inputs):
    prompt_out = prompt_head
    paragraph_list = paragraphs[i:i+number_of_inputs]
    for paragraph in paragraph_list:
        paragraph_number = paragraph[0]
        text = paragraph[1]
        people_num = paragraph[3]
        people = paragraph[2].split(",")
        alphabet = "abcdefghi"
        prompt2 = ' it mentions '
        for i in range(people_num):
            prompt2 += "[" + alphabet[i] + "]" + '"' + people[i] + '", '
        prompt2 = prompt2[:-2]
        prompt = 'Task number is {}. The biography is "{}",'.format(paragraph_number, text)
        prompt_out += prompt + prompt2 + "\n"
    
    gpt_result = []
    if os.path.isfile(folder_path+'id' + str(paragraph_number) + '.txt'):
            continue
    while True:
        try:  
            #time.sleep(1)
            account_data = forefront.Account.create(logging=False)
            print("Trying to evaluate paragraph {}".format(paragraph_number))
            response = []
            for ttt in forefront.StreamingCompletion.create(
                account_data=account_data,
                prompt=prompt_out,
                model='gpt-4'
            ):
                response.append(ttt.choices[0].text)
            response = "".join(response)
            #print(response)
            if len(response) >= 15:
                with open(folder_path+'id' + str(paragraph_number) + '.txt', 'w') as f:
                    f.write(response)
                break
        except Exception as e: # work on python 3.x
            print(e)
            if str(e) == "HTTP 429":
                print("429, need to sleep for a while")
                time.sleep(100)
            if str(e) == "HTTP 422":
                print("Need to retry, 422")
                time.sleep(2)
            
    
    result.append(response)
    
print("--- %s seconds ---" % (time.time() - start_time))
