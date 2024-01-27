import os
from time import sleep

import cv2
import pandas as pd
import pynput
from PIL import ImageGrab
from pynput.keyboard import Key, Listener
from pynput.mouse import Button

#-----------------------------------------------------------------------------

class ParsingException(Exception):
    pass

#-----------------------------------------------------------------------------

class MP_Filler:
    def __init__(self) -> None:
        self.coords = None
        self.__mouse__ = pynput.mouse.Controller()
        self.__keyboard__ = pynput.keyboard.Controller()


    def setup_coordinates(self):
        self.screenshot_path = 'screenshot.png'
        desktop_im = self.__take_screenshot__()

        self.coords = dict()

        self.coords['Create'] = self.__find_coords__(desktop_im,
                                                     'create.png')

        self.__mouse__.position = self.coords['Create']
        self.__mouse__.click(Button.left)
        sleep(1)
        desktop_fill_im = self.__take_screenshot__()

        self.coords['FIO'] = self.__find_coords__(desktop_fill_im,
                                                  'student.png',
                                                  indent=(0.75, 0.5))
        
        self.coords['Category'] = self.__find_coords__(desktop_fill_im,
                                                       'category.png',
                                                       indent=(0.25, 0.5))
        
        self.coords['Sum'] = self.__find_coords__(desktop_fill_im,
                                                  'sum.png',
                                                  indent=(0.25, 0.5))
        
        self.coords['Documents'] = self.__find_coords__(desktop_fill_im,
                                                        'docs.png',
                                                        indent=(0.95, 0.5))
        
        self.coords['Confirm'] = self.__find_coords__(desktop_fill_im,
                                                      'confirm.png')


    def fill_MP(self, table_path):
        try:
            self.__parse_table__(table_path)
        except FileNotFoundError:
            raise FileNotFoundError
        except Exception as error:
            raise ParsingException(error)

        for i, request in enumerate(self.MP_data):
            self.__fill_request__(request)
            yield {'FIO': request['FIO'],
                   'Sum': request['Sum'],
                   'Category': request['Category'],
                   'Number': i + 1,
                   'Total': len(self.MP_data)}


    def wait_confirmation(self):
        with Listener(on_press=self.__check_key__) as listener:
            listener.join()
    

    def __check_key__(self, key):
        if key == Key.shift_r:
            return False


    def __parse_table__(self, table_path: str):
        table_path = table_path.replace('"', '').strip()
        if not os.path.isfile(table_path) or not table_path.endswith('.xlsx'):
            raise FileNotFoundError

        df = pd.read_excel(table_path, sheet_name='Лист1', engine='openpyxl')

        self.MP_data = list()
        for i in df.index:
            fio = df['ФИО'][i]
            category_name = (df['Категория'][i]).strip()
            sum = int(df['Сумма'][i])

            if category_name == 'Обучающиеся, нуждающиеся в социальной помощи':
                category_number = 12
            elif category_name == 'Обучающиеся, находящиеся в тяжелом материальном положении':
                category_number = 13
            elif category_name == 'Обучающиеся, нуждающиеся в единовременной материальной поддержке':
                category_number = 14
            else:
                raise ParsingException

            self.MP_data.append({'FIO': fio,
                                 'Category_Number': category_number,
                                 'Category': category_name,
                                 'Sum': sum})
        return self.MP_data


    def __fill_request__(self, request):
        self.__mouse__.position = self.coords['FIO']
        self.__mouse__.click(Button.left)

        self.__keyboard__.type(request['FIO'])
        sleep(0.3)
        self.__keyboard__.tap(Key.enter)

        sleep(0.2)

        self.__mouse__.position = self.coords['Category']
        self.__mouse__.click(Button.left)

        sleep(0.3)

        for _ in range(20):
            self.__keyboard__.tap(Key.up)
        for _ in range(request['Category_Number']):
            self.__keyboard__.tap(Key.down)

        self.__keyboard__.tap(Key.enter)

        sleep(0.2)

        self.__mouse__.position = self.coords['Sum']
        self.__mouse__.click(Button.left)
        self.__keyboard__.type(str(request['Sum']))

        sleep(0.3)

        self.__mouse__.position = self.coords['Documents']
        self.__mouse__.click(Button.left)

        sleep(0.3)

        self.__mouse__.position = self.coords['Confirm']
        self.__mouse__.click(Button.left)

        sleep(1)

        self.__mouse__.position = self.coords['Create']
        self.__mouse__.click(Button.left)

        return request


    def __find_coords__(self, screenshot_im, template_path,
                              indent=None, threshold=0.8):
        template_path = os.path.join(os.path.dirname(__file__),
                                     'templates',
                                     template_path)
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        h, w = template.shape

        res = cv2.matchTemplate(screenshot_im, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val >= threshold:
            if indent is None:
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
            else:
                center_x = max_loc[0] + w * indent[0]
                center_y = max_loc[1] + h * indent[1]
            return center_x / 2, center_y / 2
        else:
            raise Exception(f'Coordinates of {template_path} not found!')


    def __take_screenshot__(self):
        screenshot = ImageGrab.grab()
        screenshot.save("screenshot.png")
        screenshot_im = cv2.cvtColor(cv2.imread("screenshot.png"),
                                     cv2.COLOR_BGR2GRAY)
        os.remove("screenshot.png")
        return screenshot_im
