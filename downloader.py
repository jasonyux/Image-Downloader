""" Download image according to given urls and automatically rename them in order. """
# -*- coding: utf-8 -*-
# author: Yabin Zheng
# Email: sczhengyabin@hotmail.com

from __future__ import print_function

import shutil
import imghdr
import os
import concurrent.futures
import requests
import check_no_text, file_operations

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Proxy-Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, sdch",
    # 'Connection': 'close',
}


def download_image(image_url, dst_dir, file_name, timeout=20, proxy_type=None, proxy=None):
    proxies = None
    if proxy_type is not None:
        proxies = {
            "http": proxy_type + "://" + proxy,
            "https": proxy_type + "://" + proxy
        }

    response = None
    file_path = os.path.join(dst_dir, file_name)
    try_times = 0
    while True:
        try:
            try_times += 1
            response = requests.get(
                image_url, headers=headers, timeout=timeout, proxies=proxies)
            with open(file_path, 'wb') as f:
                f.write(response.content)
            response.close()
            file_type = imghdr.what(file_path)
            # if file_type is not None:
            if file_type in ["jpg", "jpeg", "png", "bmp"]:
                # if has text in it, remove it
                ret = check_no_text.check_clean(file_path)
                if ret != 1:
                    file_operations.remove_file(file_path)
                    print("## HAS TEXT OR ERROR [{}]:  {}  {}".format(ret, file_path, image_url))
                    return 0 # removed
                else:
                    new_file_name = "{}.{}".format(file_name, file_type)
                    new_file_path = os.path.join(dst_dir, new_file_name)
                    
                    shutil.move(file_path, new_file_path)
                    print("## OK:  {}  {}".format(new_file_name, image_url))
                    return 1 # downloaded
            else:
                file_operations.remove_file(file_path)
                print("## Err:  {}".format(image_url))
            return 0 # removed
        except Exception as e:
            if try_times < 3:
                continue
            if response:
                response.close()
            file_operations.remove_file(file_path)
            print("## Fail:  {}  {}".format(image_url, e.args))
            break
    return 0


def download_images(image_urls, dst_dir, max_imgs, file_prefix="img", concurrency=50, timeout=20, proxy_type=None, proxy=None):
    """
    Download image according to given urls and automatically rename them in order.
    :param timeout:
    :param proxy:
    :param proxy_type:
    :param image_urls: list of image urls
    :param dst_dir: output the downloaded images to dst_dir
    :param file_prefix: if set to "img", files will be in format "img_xxx.jpg"
    :param concurrency: number of requests process simultaneously
    :return: none
    """

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        future_list = list()
        count = 0
        last_pos = 0
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for image_url in image_urls:
            file_name = file_prefix + "_" + "%04d" % count
            future_list.append(executor.submit(
                download_image, image_url, dst_dir, file_name, timeout, proxy_type, proxy))
            # check how many has completed
            queue_len = len(future_list)
            if queue_len > last_pos:
                to_check = queue_len - last_pos
                for _ in concurrent.futures.as_completed(future_list[-to_check:]):
                    if _.result() == 1:
                        count += 1 # successfully downloaded
                    last_pos += 1 # seen
            if count >= max_imgs:
                break
        concurrent.futures.wait(future_list, timeout=180)
        # needs to check again here
        queue_len = len(future_list)
        if queue_len > last_pos:
            to_check = queue_len - last_pos
            for _ in concurrent.futures.as_completed(future_list[-to_check:]):
                if _.result() == 1:
                    count += 1 # successfully downloaded
    return count
