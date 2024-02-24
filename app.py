import io
import sys

original_stdout = sys.stdout
original_stderr = sys.stderr

buffer = io.StringIO()
sys.stdout = sys.stderr = buffer

#------------------ IMPORTS ------------------#

import traceback

import eel

from backend import MP_Filler, ParsingException
from check_license import LicenseGDriveChecker

MPF = None

#------------------ EEL ------------------#

@eel.expose
def check_setup_py():
	if MPF.coords is None:
		eel.showAlert("Ошибка: для начала выполните настройку координат!")
		return False
	else:
		return True


@eel.expose
def fill_1C_py(table_path):
	try:
		for data in MPF.fill_MP(table_path):
			eel.updateProgressBar(data['Number'], data['Total'])
			eel.addText(f"Заявка №{data['Number']} заполнена\n" +
						f"ФИО: {data['FIO']}\n"
						f"Сумма: {data['Sum']}\n"
						f"Категория: {data['Category']}\n\n\n")
			MPF.wait_confirmation()
	except FileNotFoundError:
		message = "Файл не найден, пожалуйста, проверьте путь и попробуйте еще раз!"
		eel.showAlert(message)
		eel.setText(message)
		return
	except ParsingException as error:
		eel.showAlert("Ошибка: неправильный формат таблицы!")
		eel.setText(f"Таблица неправильного формата, пожалуйста, "
					f"проверьте ее и попробуйте еще раз!\n\n{error}")
		return
	except Exception as error:
		eel.showAlert("Не удалось заполнить заявки!")
		eel.setText("Возникла ошибка при настройке, пожалуйста, проверьте " +
					"отображается ли окно 1C и попробуйте еще раз!\n\n")
		eel.addText(f"Информация об ошибке:\n{error}\n")
		eel.addText(traceback.format_exc())
		return

	eel.setText("Таблица успешно заполнена!")


@eel.expose
def setup_coordinates_py():
	try:
		MPF.setup_coordinates()
		eel.setText("Настройка координат успешно выполнена!\n\n" +
                    "Можно приступать к заполнению.")
		eel.showAlert("Настройка координат завершена!")
	except Exception as error:
		eel.showAlert("Не удалось настроить координаты!")
		eel.setText("Возникла ошибка при настройке, пожалуйста, проверьте " +
					"отображается ли окно 1C и попробуйте еще раз!\n\n")
		eel.addText(f"Информация об ошибке:\n{error}\n")
		eel.addText(traceback.format_exc())


@eel.expose
def check_license_py(license_key):
	lgc = LicenseGDriveChecker()
	return lgc.check_license(license_key)


@eel.expose
def check_active_license_py():
	lgc = LicenseGDriveChecker()
	return lgc.check_active_license()


#------------------ MAIN ------------------#

def main():
	global MPF
	MPF = MP_Filler()

	eel.init('web')

	sys.stdout = original_stdout
	sys.stderr = original_stderr

	eel.start('index.html', mode='edge', port=8080)


if __name__ == '__main__':
	main()