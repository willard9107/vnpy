"""
Author: shifulin
Email: shifulin666@qq.com
"""
from mxw.utils.common_import import *
# python3
from io import BytesIO

from requests import session
from PIL import Image
import PIL.ImageOps
import pytesseract


def reg_img(file_obj):
    im = Image.open(file_obj)
    im = im.convert('L')
    binary_image = im.point([0 if i < 210 else 1 for i in range(256)], '1')
    im1 = binary_image.convert('L')
    im2 = PIL.ImageOps.invert(im1)
    im3 = im2.convert('1')
    im4 = im3.convert('L')
    res = pytesseract.image_to_string(im4)
    # print(res)
    # im4.show()
    return res


def flag_filter(content, flag):
    result = content.split(flag)[1].split('"')[0]
    return result


def get_current_equity(content):
    a = content[content.find('客户权益'):]
    b = a.split('<td class="table-normal-text" align="right">')[1]
    c = b[:b.find('&nbsp;')].strip()
    d = ''.join(c.split(','))
    return float(d)


def do(user_id, passwd):
    header = {
        'Connection': 'keep-alive',
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    }
    url = "https://investorservice.cfmmc.com/login.do"
    token_flag = 'name="org.apache.struts.taglib.html.TOKEN" value="'
    veri_code_flag = 'src="/veriCode.do?t='
    ss = session()
    res = ss.get(url, headers=header)
    content = res.content.decode()
    token = flag_filter(content, token_flag)
    veri_code_url = 'https://investorservice.cfmmc.com/veriCode.do?t=' + flag_filter(content, veri_code_flag)
    for i in range(200):
        print(f'第{i + 1}次尝试识别验证码')
        try:
            tmp_file = BytesIO()
            tmp_file.write(ss.get(veri_code_url).content)
            veri_code = reg_img(tmp_file)
            if veri_code and len(veri_code) == 6:
                veri_code = ''.join(filter(str.isalnum, veri_code))
                print('\t验证码：', veri_code)
                post_data = {
                    "org.apache.struts.taglib.html.TOKEN": token,
                    "showSaveCookies": '',
                    "userID": user_id,
                    "password": passwd,
                    "vericode": veri_code,
                }
                content2 = ss.post(url, data=post_data, headers=header, timeout=5)
                res = content2.content.decode()
                if "验证码错误" not in res:
                    # print('页面:', res)
                    current_equity = get_current_equity(res)
                    print('爬取客户权益 成功')
                    print(f'账户:{user_id}  客户权益:{current_equity}')
                    return
            m_time.sleep(1)
            veri_code_url = "https://investorservice.cfmmc.com/veriCode.do?t=" + str(int(m_time.time() * 1000))
        except Exception as e:
            print(e)
    print('爬取客户权益 失败')


if __name__ == '__main__':
    # 账号
    account = '0078901801201'
    # 密码
    password = 'T3f6WNrgwdmH'
    do(account, password)