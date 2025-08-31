import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def read_urls_from_file(filename):
    """从文件中读取URL列表"""
    urls = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):  # 跳过空行和注释
                    urls.append(line)
        return urls
    except FileNotFoundError:
        print(f"错误：找不到文件 {filename}")
        return []

def setup_driver():
    """设置Chrome WebDriver"""
    chrome_options = Options()
    # chrome_options.add_argument('--headless')  # 取消注释可启用无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def wait_for_test_completion(driver, timeout=60):
    """等待测速完成"""
    try:
        # 等待加载动画消失或结果出现
        start_time = time.time()
        
        # 先等待至少10秒，确保测速有足够时间
        time.sleep(10)
        
        # 然后检查结果是否已经出现
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "return_info"))
        )
        
        # 额外等待2秒确保结果完全加载
        time.sleep(2)
        
        return True
    except Exception as e:
        print(f"等待测速完成时超时或出错: {str(e)}")
        return False

def run_speed_test(driver, url):
    """对单个URL运行测速测试"""
    try:
        print(f"开始测试: {url}")
        
        # 打开测速网站
        driver.get("https://www.itdog.cn/http/")
        
        # 等待页面加载完成
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "host"))
        )
        
        # 清空输入框并输入URL
        input_field = driver.find_element(By.ID, "host")
        input_field.clear()
        input_field.send_keys(url)
        
        # 点击测速按钮
        speed_test_button = driver.find_element(By.XPATH, "//a[@onclick=\"check_form('fast')\"]")
        speed_test_button.click()
        
        print("测速中，请等待10秒以上...")
        
        # 等待测速完成
        if wait_for_test_completion(driver):
            # 获取结果
            result_element = driver.find_element(By.ID, "return_info")
            result = result_element.text
            
            # 获取测速时间（如果有显示的话）
            try:
                time_element = driver.find_element(By.CLASS_NAME, "time")
                test_time = time_element.text
                result = f"测速时间: {test_time}\n{result}"
            except:
                pass
                
            return result
        else:
            return "测速超时或未能获取结果"
            
    except Exception as e:
        return f"测试过程中出现错误: {str(e)}"

def main():
    # 读取URL列表
    urls = read_urls_from_file("dependency.txt")
    
    if not urls:
        print("没有找到有效的URL，请检查dependency.txt文件")
        return
    
    print(f"找到 {len(urls)} 个URL进行测试")
    
    # 设置WebDriver
    driver = setup_driver()
    
    try:
        # 对每个URL进行测试
        results = []
        for i, url in enumerate(urls, 1):
            print(f"\n正在测试第 {i}/{len(urls)} 个URL")
            result = run_speed_test(driver, url)
            
            results.append({
                'url': url,
                'result': result
            })
            
            print(f"测试完成: {url}")
            print(f"结果摘要: {result[:100]}..." if len(result) > 100 else f"结果: {result}")
            print("-" * 80)
            
            # 等待一下再进行下一个测试
            time.sleep(3)
        
        # 打印所有结果
        print("\n" + "="*80)
        print("测速结果汇总:")
        print("="*80)
        for i, res in enumerate(results, 1):
            print(f"{i}. URL: {res['url']}")
            print(f"结果:\n{res['result']}")
            print("-" * 80)
            
    except KeyboardInterrupt:
        print("\n用户中断测试")
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
    finally:
        # 关闭浏览器
        driver.quit()
        print("浏览器已关闭")

if __name__ == "__main__":
    main()
