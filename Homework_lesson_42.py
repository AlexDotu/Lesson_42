import random
import re
import time

from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def price_sorting():
    driver.get(url="https://www.datart.cz/")
    time.sleep(3)

    try:
        driver.find_element(By.XPATH, '//*[@id="c-p-bn"]').click()
        print("Кнопка согласия с куки нажата")
    except Exception as e:
        print(f"Ошибка при нажатии на кнопку согласия с куки: {e}")
    time.sleep(3)

    try:
        # Находим элементы категорий на странице
        categories = driver.find_elements(By.XPATH, "//li[@class='main-menu-catalog-category']")
        if len(categories) > 0:
            random_category = random.choice(categories)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", random_category)
            driver.execute_script("arguments[0].focus();", random_category)
            random_category.click()
            time.sleep(5)
            print("categories === OK")
        else:
            print("No categories found.")
            driver.quit()
            return

        # Начала вылезать реклама, поэтому обходим это окно - пробуем закрыть overlay, если оно существует
        try:
            overlay = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@class="screen-overlay active"]')))
            driver.execute_script("arguments[0].click();", overlay)  # Используем JS для клика
            print("Overlay закрыто.")
        except Exception:
            print("Overlay не найдено, продолжаем.")

        # Ожидание появления подкатегорий
        try:
            refresh_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "snippet--login-refresh"))
            )
            subcategories = refresh_container.find_elements(By.XPATH, "//div[@class='category-tree-box bg-white']")

            if len(subcategories) > 0:
                random_subcategory = random.choice(subcategories)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", random_subcategory)
                driver.execute_script("arguments[0].focus();", random_subcategory)
                time.sleep(3)

                try:
                    random_subcategory.click()
                except ElementClickInterceptedException:
                    print("Элемент был перекрыт другим. Используем JS для клика.")
                    driver.execute_script("arguments[0].click();", random_subcategory)
                except ElementNotInteractableException:
                    print("Элемент не взаимодействует. Пробуем прокрутить страницу и кликнуть снова.")
                    driver.execute_script("arguments[0].scrollIntoView(true);", random_subcategory)
                    random_subcategory.click()

                time.sleep(3)
                print("subcategories === OK")
            else:
                print("No subcategories found.")
                driver.quit()
                return
        except Exception as e:
            print(f"Ошибка при загрузке подкатегорий: {e}")
            return

        try:
            product_names = driver.find_elements(By.XPATH, '//*[@class="item-title"]')
            product_descriptions = driver.find_elements(By.XPATH, '//*[@class="item-description"]')
            product_prices = driver.find_elements(By.XPATH, '//*[@class="actual "]')

            print(product_names, product_descriptions, product_prices)

            if not product_names:
                print("Не удалось найти товары.")
                return

            with open('products.txt', 'w', encoding='utf-8') as file:
                for name, description, price in zip(product_names, product_descriptions, product_prices):
                    product_name = name.text.strip()
                    product_description = description.text.strip()
                    product_price = re.sub(r'[^\d.,]', '', price.text).replace(",", ".").strip() + " CZK"

                    file.write(f"Название: {product_name}\n")
                    file.write(f"Описание: {product_description}\n")
                    file.write(f"Цена: {product_price}\n")
                    file.write("----\n")

            print("Данные сохранены в файл 'products.txt'.")
        except Exception as e:
            print(f"Ошибка при извлечении товаров или записи в файл: {e}")

    except Exception as ex:
        print(f"Произошла ошибка: {ex}")
    finally:
        driver.close()
        driver.quit()


price_sorting()
