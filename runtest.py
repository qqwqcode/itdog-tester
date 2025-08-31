import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def read_urls_from_file(filename):
    """从文件中读取URL列表"""
    urls = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):  # 跳过空行和注释
                    urls.append(line)
        return urls
    except FileNotFoundError:
        print(f"错误：找不到文件 {filename}")
        return []
    except Exception as e:
        print(f"读取文件时出错: {str(e)}")
        return []

def setup_driver():
    """设置Chrome WebDriver，兼容本地和CI环境"""
    chrome_options = Options()
    
    # 针对CI环境的配置
    if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
        print("检测到CI环境，使用无头模式")
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        chrome_options.add_argument('--disable-infobars')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
    else:
        # 本地环境配置
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        # 在CI环境中使用webdriver-manager自动管理驱动版本
        if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            driver = webdriver.Chrome(options=chrome_options)
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"初始化WebDriver时出错: {str(e)}")
        # 尝试备用方案
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except:
            raise

def wait_for_test_completion(driver, timeout=15):
    """等待测速完成 - 简单等待固定时间"""
    try:
        print(f"等待测速完成，预计需要{timeout}秒...")
        time.sleep(timeout)  # 直接等待固定时间
        return True
    except Exception as e:
        print(f"等待测速完成时出错: {str(e)}")
        return False

def run_speed_test(driver, url):
    """对单个URL运行测速测试"""
    try:
        print(f"开始测试: {url}")
        
        # 打开测速网站
        driver.get("https://www.itdog.cn/http/")
        
        # 等待页面加载完成
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "host"))
        )
        
        # 清空输入框并输入URL
        input_field = driver.find_element(By.ID, "host")
        input_field.clear()
        input_field.send_keys(url)
        
        # 点击测速按钮
        speed_test_button = driver.find_element(By.XPATH, "//a[@onclick=\"check_form('fast')\"]")
        speed_test_button.click()
        
        print("测速中，请等待...")
        
        # 等待测速完成
        if wait_for_test_completion(driver, timeout=15):
            # 获取结果
            try:
                result_element = driver.find_element(By.ID, "return_info")
                result = result_element.text
                
                # 获取测速时间（如果有显示的话）
                try:
                    time_element = driver.find_element(By.CLASS_NAME, "time")
                    test_time = time_element.text
                    result = f"测速时间: {test_time}\n{result}"
                except NoSuchElementException:
                    pass
                    
                return result
            except NoSuchElementException:
                # 尝试其他可能的选择器
                try:
                    result_element = driver.find_element(By.CLASS_NAME, "result-content")
                    return result_element.text
                except:
                    return "无法找到结果元素，页面结构可能已更改"
        else:
            return "测速超时或未能获取结果"
            
    except Exception as e:
        return f"测试过程中出现错误: {str(e)}"

def save_results_to_file(results, filename="speed_test_results.txt"):
    """将结果保存到文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("测速结果汇总\n")
            f.write("="*80 + "\n")
            for i, res in enumerate(results, 1):
                f.write(f"{i}. URL: {res['url']}\n")
                f.write(f"结果:\n{res['result']}\n")
                f.write("-" * 80 + "\n")
        print(f"结果已保存到 {filename}")
    except Exception as e:
        print(f"保存结果到文件时出错: {str(e)}")

def main():
    # 读取URL列表
    urls = read_urls_from_file("dependency.txt")
    
    if not urls:
        print("没有找到有效的URL，请检查dependency.txt文件")
        return
    
    print(f"找到 {len(urls)} 个URL进行测试")
    
    # 设置WebDriver
    try:
        driver = setup_driver()
    except Exception as e:
        print(f"无法启动浏览器: {str(e)}")
        print("在CI环境中，请确保已正确配置Chrome")
        return
    
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
            time.sleep(2)
        
        # 打印所有结果
        print("\n" + "="*80)
        print("测速结果汇总:")
        print("="*80)
        for i, res in enumerate(results, 1):
            print(f"{i}. URL: {res['url']}")
            print(f"结果:\n{res['result']}")
            print("-" * 80)
            
        # 保存结果到文件
        save_results_to_file(results)
            
    except KeyboardInterrupt:
        print("\n用户中断测试")
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
    finally:
        # 关闭浏览器
        try:
            driver.quit()
            print("浏览器已关闭")
        except:
            pass

if __name__ == "__main__":
    main()
