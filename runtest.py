import time
import os
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 配置参数
REFRESH_INTERVAL = 2  # 刷新间隔（秒）
TOTAL_REFRESH_COUNT = 160  # 总刷新次数
WAIT_AFTER_TEST = 18  # 每次测速后等待时间（秒）

def ensure_result_directory():
    """确保结果目录存在"""
    result_dir = "result"
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
        print(f"创建结果目录: {result_dir}")
    return result_dir

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
    """设置Chrome WebDriver"""
    chrome_options = Options()
    
    # 浏览器设置
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
    except Exception as e:
        print(f"使用默认ChromeDriver失败: {str(e)}")
        try:
            service = Service(executable_path='/usr/bin/chromedriver')
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e2:
            print(f"使用系统chromedriver也失败: {str(e2)}")
            raise

def wait_for_test_completion(driver, timeout=60):
    """等待测速完成"""
    try:
        print(f"等待测速完成，预计需要{timeout}秒...")
        time.sleep(timeout)
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
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "host"))
        )
        
        # 清空输入框并输入URL
        input_field = driver.find_element(By.ID, "host")
        input_field.clear()
        input_field.send_keys(url)
        
        # 直接触发JavaScript事件
        print("触发测速事件...")
        driver.execute_script("check_form('fast')")
        
        print("测速中，请等待...")
        
        # 等待测速完成
        if wait_for_test_completion(driver, timeout=WAIT_AFTER_TEST):
            # 获取结果
            try:
                result_element = driver.find_element(By.ID, "return_info")
                result = result_element.text
                
                # 获取测速时间
                try:
                    time_element = driver.find_element(By.CLASS_NAME, "time")
                    test_time = time_element.text
                    result = f"测速时间: {test_time}\n{result}"
                except NoSuchElementException:
                    pass
                    
                return result
            except NoSuchElementException:
                return "无法找到结果元素"
        else:
            return "测速超时"
            
    except Exception as e:
        return f"测试过程中出现错误: {str(e)}"

def save_single_result(result_dir, url, result, refresh_count, test_count):
    """保存单次测试结果到文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{result_dir}/{url.replace('://', '_').replace('/', '_').replace(':', '_')}_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"URL: {url}\n")
            f.write(f"刷新次数: {refresh_count}\n")
            f.write(f"测试序号: {test_count}\n")
            f.write("="*50 + "\n")
            f.write(result + "\n")
        return filename
    except Exception as e:
        print(f"保存结果到文件时出错: {str(e)}")
        return None

def save_summary_result(result_dir, all_results):
    """保存汇总结果"""
    summary_file = f"{result_dir}/summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("测速结果汇总\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总测试次数: {len(all_results)}\n")
            f.write("="*80 + "\n\n")
            
            for i, res in enumerate(all_results, 1):
                f.write(f"{i}. URL: {res['url']}\n")
                f.write(f"   测试时间: {res['timestamp']}\n")
                f.write(f"   刷新次数: {res['refresh_count']}\n")
                f.write(f"   测试序号: {res['test_count']}\n")
                f.write(f"   结果:\n{res['result']}\n")
                f.write("-" * 80 + "\n")
        
        print(f"汇总结果已保存到: {summary_file}")
        return summary_file
    except Exception as e:
        print(f"保存汇总结果时出错: {str(e)}")
        return None

def main():
    # 确保结果目录存在
    result_dir = ensure_result_directory()
    
    # 读取URL列表
    urls = read_urls_from_file("dependency.txt")
    
    if not urls:
        print("没有找到有效的URL，请检查dependency.txt文件")
        return
    
    print(f"找到 {len(urls)} 个URL进行测试")
    print(f"刷新间隔: {REFRESH_INTERVAL}秒")
    print(f"总刷新次数: {TOTAL_REFRESH_COUNT}次")
    print(f"结果将保存到: {result_dir}目录")
    
    # 设置WebDriver
    try:
        driver = setup_driver()
    except Exception as e:
        print(f"无法初始化WebDriver: {str(e)}")
        return
    
    all_results = []
    refresh_count = 0
    test_count = 0
    
    try:
        while refresh_count < TOTAL_REFRESH_COUNT:
            refresh_count += 1
            print(f"\n{'='*60}")
            print(f"开始第 {refresh_count}/{TOTAL_REFRESH_COUNT} 轮刷新测试")
            print(f"{'='*60}")
            
            # 对每个URL进行测试
            for i, url in enumerate(urls, 1):
                test_count += 1
                print(f"\n正在测试第 {i}/{len(urls)} 个URL (总测试序号: {test_count})")
                
                result = run_speed_test(driver, url)
                
                # 保存单次结果
                saved_file = save_single_result(result_dir, url, result, refresh_count, test_count)
                if saved_file:
                    print(f"结果已保存到: {saved_file}")
                
                all_results.append({
                    'url': url,
                    'result': result,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'refresh_count': refresh_count,
                    'test_count': test_count
                })
                
                print(f"测试完成: {url}")
                print(f"结果摘要: {result[:100]}..." if len(result) > 100 else f"结果: {result}")
                print("-" * 60)
            
            # 如果不是最后一次刷新，等待下一次刷新
            if refresh_count < TOTAL_REFRESH_COUNT:
                print(f"\n等待 {REFRESH_INTERVAL} 秒后进行下一次刷新...")
                for remaining in range(REFRESH_INTERVAL, 0, -1):
                    print(f"\r剩余等待时间: {remaining}秒", end='', flush=True)
                    time.sleep(1)
                print("\n开始下一次刷新...")
                
                # 刷新浏览器
                driver.refresh()
                time.sleep(3)  # 等待刷新完成
        
        # 保存汇总结果
        summary_file = save_summary_result(result_dir, all_results)
        
        # 打印最终统计
        print(f"\n{'='*80}")
        print("所有测试完成！")
        print(f"总刷新次数: {refresh_count}")
        print(f"总测试次数: {test_count}")
        print(f"结果文件保存在: {result_dir}目录")
        if summary_file:
            print(f"汇总文件: {summary_file}")
        print(f"{'='*80}")
            
    except KeyboardInterrupt:
        print("\n用户中断测试")
        # 保存已完成的测试结果
        if all_results:
            save_summary_result(result_dir, all_results)
    except Exception as e:
        print(f"程序运行出错: {str(e)}")
        if all_results:
            save_summary_result(result_dir, all_results)
    finally:
        # 关闭浏览器
        if 'driver' in locals():
            driver.quit()
            print("浏览器已关闭")

if __name__ == "__main__":
    main()
