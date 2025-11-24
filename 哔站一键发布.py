from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import time
import json
from images import get_image
from translate import chanslater,describer
import os
def bilibili_publish(space_name,video_path,collection_text,content_text,file_title):
    options=Options()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-infobars')
    #options.add_argument('--headless')
    options.add_argument(f'user-agent={UserAgent.random}')
    
    # 添加更多反反爬机制
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("dom.webnotifications.enabled", False)
    
    driver=webdriver.Firefox(options=options)
    url=f"https://member.bilibili.com/platform/upload/video/frame"
    driver.get(url=url)
    with open("all_cookies.json", "r", encoding="utf-8") as f:
        web_cookies = json.load(f)
    for cookie in web_cookies["bilibili_msg"]:
        driver.add_cookie(cookie)
    driver.get(url=url)
    wait=WebDriverWait(driver, 800)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,".upload-area")))
    driver.find_element(By.CSS_SELECTOR,".bcc-upload-wrapper > input:nth-child(2)").send_keys(video_path)
    # 输入标题
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,".input-instance:nth-child(1) > input:nth-child(1)")))
    title=driver.find_element(By.CSS_SELECTOR,"div.input-instance:nth-child(1) > input:nth-child(1)")
    title.clear()
    best_prompt=f'视频分区：{space_name}视频原标题：{file_title}\n视频内容：{content_text}'
    best_title=chanslater(best_prompt)
    print(best_title)
    title.send_keys(best_title)
    # 上传封面
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"div.img:nth-child(1)"))).click()#.cover-select-footer-upload > div:nth-child(1) > div:nth-child(1) > button:nth-child(1)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"div.cover-select-header-tab-item:nth-child(2) > div:nth-child(1)"))).click()
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,".cover-select-footer-upload > div:nth-child(1) > div:nth-child(1) > button:nth-child(1)")))
    post_img=driver.find_element(By.CSS_SELECTOR,".cover-select-footer-upload > div:nth-child(1) > div:nth-child(1) > input:nth-child(2)")
    
    img_path,prompt=get_image(prompt=best_prompt,title=best_title)
    print("封面提示词：",prompt)
    post_img.send_keys(img_path)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,".cover-select-footer-pick > button:nth-child(2)"))).click()
    time.sleep(2)
    # 选择分区
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"div.select-container:nth-child(1) > div:nth-child(1)"))).click()
    time.sleep(1)
    '''
    divide_spaces=driver.find_elements(By.XPATH,"/html/body/div/div[2]/div[4]/div[2]/div/div/div/micro-app/micro-app-body/div[1]/div[2]/div[1]/div[2]/div[5]/div/div[2]/div/div[2]/div/div")
    for space in divide_spaces:
        time.sleep(0.5)
        if space.text==space_name:
            try:
                space.click()
            except:
                continue
    time.sleep(1)'''
    # 选择标签
    tags=driver.find_elements(By.XPATH,"/html/body/div/div[2]/div[4]/div[2]/div/div/div/micro-app/micro-app-body/div[1]/div[2]/div[1]/div[2]/div[6]/div/div[2]/div/div")
    for tag in tags:
        try:
            tag.click()
        except:
            continue
    # 输入描述
    description=driver.find_element(By.CSS_SELECTOR,".desc-text-wrp > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)")
    description.click()
    des=describer(best_prompt)
    print("描述：",des)
    description.send_keys(des) 
    # 选择合集
    driver.find_element(By.CSS_SELECTOR,"div.video-season-content:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > span:nth-child(1)").click()  
    collections=driver.find_elements(By.XPATH,"/html/body/div/div[2]/div[4]/div[2]/div/div/div/micro-app/micro-app-body/div[1]/div[2]/div[1]/div[2]/div[10]/div/div[2]/div/div/div[2]/div[2]/div")
    for collection in collections:
        if collection.text==collection_text:
            time.sleep(0.5)
            collection.click()
            break
    # 发布
    publish_btn=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,".submit-add")))
    #publish_btn.click()
    #time.sleep(1)
    #driver.quit()
if __name__ == "__main__":
    videos_path=r"D:\AI\油管视频汉化\subtitles\竖屏"
    files=os.listdir(videos_path)
    for file in files:
        if file.endswith(".mp4"):
            file_text=file.replace("_with_subtitles_final.mp4","")
            text_file=file.replace("_with_subtitles_final.mp4","_en.txt")
            print(file_text,text_file)
            with open(os.path.join(videos_path,text_file),"r",encoding="utf-8") as f:
                text_file=f.read()
            bilibili_publish(space_name="科技数码",video_path=os.path.join(videos_path,file),content_text=text_file,file_title=file_text,collection_text="竖屏")