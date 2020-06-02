import browser_cookie3
import urllib3
import requests
import re
import time
import random
import sys
import colorama
from bs4 import BeautifulSoup
from __banner.banner import banner
from __colors__.colors import *
from __functions.functions import *
from __constants.constants import CHECKOUT, total_sites, site_range
from urllib.parse import urlsplit, parse_qs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

func_list = [
    lambda page : learnviral(page),
    lambda page : discudemy(page),
    lambda page : udemy_freebies(page),
    lambda page : udemy_coupons_me(page),
    lambda page : real_disc(page)
]

def get_course_id(url, cookies):
    global purchased_text
    r2 = requests.get(url, verify=False, cookies=cookies)
    soup = BeautifulSoup(r2.content, 'html.parser')
    try:
        purchased_text = soup.find('div', class_ = 'purchase-text').text.replace("\n","")
    except:
        purchased_text = ''
    try:
        courseid = soup.find('div', class_ = 'full-width full-width--streamer streamer--complete')['data-course-id']
    except:
        try:
            courseid = soup.find('div', class_ = 'udlite-full-width-container')['data-course-id']
        except:
            purchased_text = 'This course is no longer accepting enrollments'
            courseid = ''
    
    return courseid


def get_course_coupon(url):
    query = urlsplit(url).query
    params = parse_qs(query)
    try:
        params = {k: v[0] for k, v in params.items()}
        return params['couponCode']
    except:
        return ''

def free_checkout(CHECKOUT, access_token, csrftoken, coupon, courseID, cookies):
    payload = '{"shopping_cart":{"items":[{"buyableType":"course","buyableId":' + str(courseID) + ',"discountInfo":{"code":"' + coupon + '"},"purchasePrice":{"currency":"INR","currency_symbol":"","amount":0,"price_string":"Free"},"buyableContext":{"contentLocaleId":null}}]},"payment_info":{"payment_vendor":"Free","payment_method":"free-method"}}'
    ip = ".".join(map(str, (random.randint(0, 255) 
                        for _ in range(4))))
    head = {
        'authorization': 'Bearer ' + access_token,
        'accept': 'application/json, text/plain, */*',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        'x-csrftoken': csrftoken,
        'x-forwarded-for': str(ip),
        'x-udemy-authorization': 'Bearer ' + access_token,
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://www.udemy.com',
        'referer': 'https://www.udemy.com/',
        'Content-Length': str(len(payload))
    }

    r = requests.post(CHECKOUT, headers=head, data=payload, cookies=cookies, verify=False)
    return r.json()

def free_enroll(courseID, access_token, cookies, csrftoken):
    head = {
        'authorization': 'Bearer ' + access_token,
        'accept': 'application/json, text/plain, */*',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
        'x-csrftoken': csrftoken,
        'x-udemy-authorization': 'Bearer ' + access_token,
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://www.udemy.com',
        'referer': 'https://www.udemy.com/'
    }

    r = requests.get('https://www.udemy.com/course/subscribe/?courseId=' + str(courseID), headers=head, verify=False, cookies=cookies)
    
    r2 = requests.get('https://www.udemy.com/api-2.0/users/me/subscribed-courses/' + str(courseID) + '/?fields%5Bcourse%5D=%40default%2Cbuyable_object_type%2Cprimary_subcategory%2Cis_private', headers=head, verify=False, cookies=cookies)
    return r2.json()

def auto_add(list_st, cookies, access_token, csrftoken):
    print('\n')
    index = 0
    global count
    while index <= len(list_st) - 1:
        sp1 = list_st[index].split('||')
        print(fc + sd + '[' + fm + sb + '*' + fc + sd + '] ' + fr + str(index + 1), fy + sp1[0], end='')

        link = list_st[index].split('||')[1]
        couponID = get_course_coupon(link)
        course_id = get_course_id(link, cookies)

        if couponID != '' and purchased_text == '':
            slp = ''
            js = free_checkout(CHECKOUT, access_token, csrftoken, couponID, course_id, cookies)

            try:
                if js['status'] == 'succeeded':
                    print(fg + ' Successfully Enrolled To Course')
                    count += 1
                    index += 1
            except:
                try:
                    msg = js['detail']
                    print(' ' + fr + msg)
                    slp = int(re.search(r'\d+', msg).group(0))
                    # index -= 1
                except:
                    print(fr + ' Expired Coupon ' + js['message'])
                    index += 1
            else:
                try:
                    if js['status'] == 'failed':
                        print(fr + ' Coupon Expired :( ')
                        index += 1
                except:
                    bnn = ''
            if slp != '':
                slp += 10
                print(fc + sd + '----' + fm + sb + '>>' +  fb + ' Pausing execution of script for ' + fr + str(slp) + ' seconds')
                time.sleep(slp)
            else:
                time.sleep(5)

        elif couponID == '' and purchased_text == '':
            js = free_enroll(course_id, access_token, cookies, csrftoken)
            try:
                if js['_class'] == 'course':
                    print(fg + ' Successfully Subscribed')
                    count += 1
                    index += 1
            except:
                print(fb + ' COUPON MIGHT HAVE EXPIRED')
                index += 1
        else:
            print(' ' + fc + purchased_text)
            index += 1
    print('\n' + fc + sd + '[' + fm + sb + '*' + fc + sd + '] ' + bc + fw + sb + 'Total Courses Subscribed: ' + str(count))

def process(list_st, dd, limit, site_index, cookies, access_token, csrftoken):
    global d
    print('\n')
    for index, stru in enumerate(list_st, start=1):
        sp1 = stru.split('||')
        print(fc + sd + '[' + fm + sb + '*' + fc + sd + '] ' + fr + str(index), fy + sp1[0])
    print('\n' + fc + sd + '----' + fm + sb + '>>' + fb + ' To load more input "m" OR to subscribe any course from above input "y": ', end='')
    input_2 = input()
    if input_2 == 'm':
        if dd != limit-1:
            return total_sites[site_index + 1]
    elif input_2 == 'y':
        try:
            subs = int(input('\n---->> Enter id of course ex - 1 or 2 or 3.... : '))
        except Exception as e:
            print('\n' + fc + sd + '[' + fm + sb + '*' + fc + sd + '] ' + fr + 'Enter Correct ID')
            subs = ''
        # print(type(subs))
        if isinstance(subs, int):
            link = list_st[subs-1].split('||')[1]
            couponID = get_course_coupon(link)
            course_id = get_course_id(link, cookies)
            if couponID != '' and purchased_text == '':
                js = free_checkout(CHECKOUT, access_token, csrftoken, couponID, course_id, cookies)
                try:
                    if js['status'] == 'succeeded':
                        print(fc + sd + '[' + fm + sb + '*' + fc + sd + '][' + fm + sb + '*' + fc + sd + ']' + fg + ' Successfully Enrolled To Course')
                except:
                    print(js['message'])
            elif couponID == '' and purchased_text == '':
                js = free_enroll(course_id, access_token, cookies, csrftoken)
                try:
                    if js['_class'] == 'course':
                        print('\n' + fc + sd + '[' + fm + sb + '*' + fc + sd + '][' + fm + sb + '*' + fc + sd + ']' + fg + ' Successfully Subscribed')
                except:
                    print('\n' + fc + sd + '[' + fm + sb + '*' + fc + sd + ']' + fr + ' COUPON MIGHT HAVE EXPIRED')
            else:
                print(fc + sd + '[' + fm + sb + '*' + fc + sd + '][' + fm + sb + '*' + fc + sd + ']' + fc + purchased_text)
        d = dd - 1
    else:
        exit()

def main():
    sys.stdout.write(banner())
    cookies = browser_cookie3.chrome(domain_name='www.udemy.com')
    my_cookies = requests.utils.dict_from_cookiejar(cookies)
    try:
        access_token = my_cookies['access_token']
        csrftoken = my_cookies['csrftoken']

    except Exception as e:
        print('\n' + fc + sd + '[' + fm + sb + '*' + fc + sd + '] ' + fr + 'Make sure you are logged in to udemy.com in chrome browser')
        access_token = ''
    if access_token != '':
        print('\n' + fc + sd + '[' + fm + sb + '*' + fc + sd + '] ' + fg +'Auto Login Successful! \n')
        time.sleep(0.8)
        print(fc + sd + '[' + fm + sb + '*' + fc + sd + '] ' + fw + 'Websites Available: ')
        bad_colors = ['BLACK', 'WHITE', 'LIGHTBLACK_EX', 'RESET']
        codes = vars(colorama.Fore)
        colors = [codes[color] for color in codes if color not in bad_colors]
        for site in total_sites:
            print(random.choice(colors) + site)
        
        print('\n' + fc + sd + '----' + fm + sb + '>>' + fb + ' Want to see available coupons (INPUT "n") OR subscribe to all available courses automatically (input "y"): ', end='')
        input_1 = input()
        more = ''

        if input_1 == 'n':
            global d
            d = 1
            for site_index, site in enumerate(total_sites):
                if site == 'Learn Viral':
                    limit = 10
                    print('\n' + fc + sd + '-------' + fm + sb + '>>' + fb +' Learn Viral ' + fm + sb + '<<' + fc + sd + '-------\n')
                    while d <= limit:
                        list_st = learnviral(d)
                        site = process(list_st, d, limit, site_index, cookies, access_token, csrftoken)
                        d += 1
                if site == 'Discudemy':
                    limit = 4
                    print('\n' + fc + sd + '-------' + fm + sb + '>>' + fb +' Discudemy ' + fm + sb + '<<' + fc + sd + '-------\n')
                    while d <= limit:
                        list_st = discudemy(d)
                        site = process(list_st, d, limit, site_index)
                        d += 1
                if site == 'Udemy Freebies':
                    limit = 4
                    print('\n' + fc + sd + '-------' + fm + sb + '>>' + fb +' Udemy Freebies ' + fm + sb + '<<' + fc + sd + '-------\n')
                    while d <= limit:
                        list_st = udemy_freebies(d)
                        site = process(list_st, d, limit, site_index)
                        d += 1
                if site == 'Udemy Coupons':
                    limit = 4
                    print('\n' + fc + sd + '-------' + fm + sb + '>>' + fb +' Udemy Coupons ' + fm + sb + '<<' + fc + sd + '-------\n')
                    while d <= limit:
                        list_st = udemy_coupons_me(d)
                        site = process(list_st, d, limit, site_index)
                        d += 1
                if site == 'Real Discount':
                    limit = 4
                    print('\n' + fc + sd + '-------' + fm + sb + '>>' + fb +' Real Discount ' + fm + sb + '<<' + fc + sd + '-------\n')
                    while d <= limit:
                        list_st = real_disc(d)
                        site = process(list_st, d, limit, site_index)
                        d += 1
        elif input_1 == 'y':
            global count
            count = 0
            for index, items in enumerate(func_list):
                print('\n' + fc + sd + '-------' + fm + sb + '>> ' + fb + total_sites[index] + fm + sb + ' <<' + fc + sd + '-------\n')
                limit = site_range[index]
                for d in range(1, limit):
                    list_st = items(d)
                    auto_add(list_st, cookies, access_token, csrftoken)
    # else:
    #     print('Make sure you are logged in to udemy.com in chrome browser')

if __name__ == '__main__':
    main()