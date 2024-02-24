async function setupCoords() {
	if (!await checkLicense()) {
		return;
	}

	let confirmText = "Будет произведена настройка координат.\n\n" +
		"Пожалуйста, откройте окно 1С, чтобы оно занимало приблизительно " +
		"половину экрана, откройте в нем раздел " +
		"'Заявка на мат. помощь', чтобы отображался список и нажмите 'ОК'\n\n" +
		"Обратите внимание, что при настройке нельзя пользоваться мышью!"

	if (confirm(confirmText)) {
		setText("Производится настройка, пожалуйста, подождите...");

		await eel.setup_coordinates_py()();
	}
	else {
		alert("Настройка координат отменена...")
	}

}

async function fill1C() {
	if (!await checkLicense()) {
		return;
	}

	if (await eel.check_setup_py()() == false) {
		return;
	}

	const filePath = window.prompt("Скопируйте путь к таблице и вставьте в поле ввода");

	if (!filePath) {
		alert("Необходимо ввести путь к таблице!");
		return;
	}

	let intro_text = "Начинаю процесс автозаполнения, пожалуйста, не трогайте " +
		"без необходимости мышь и клавиатуру. После каждой " +
		"заполненной заявки для продолжения нажмите на правый 'Shift'.\n\n";
	setText(intro_text);

	const progressBarContainer = document.querySelector('.progress-bar-container');
	progressBarContainer.style.display = 'block';

	await eel.fill_1C_py(filePath)();

	progressBarContainer.style.display = 'none';
}

async function checkLicense() {
	if (await eel.check_active_license_py()()) {
		return true;
	}

	const license_key = window.prompt("Введите лицензионный ключ");
	if (!license_key) {
		alert("Необходимо ввести лицензионный ключ!");
		return false;
	}

	if (await eel.check_license_py(license_key)()) {
		alert("Лицензионный ключ подтвержден!");
		return true;
	}
	else {
		alert("Лицензионный ключ неверный!");
		return false;
	}
}

eel.expose(addText);
function addText(text) {
	var outputTextarea = document.getElementById("output");
	outputTextarea.value += text + '\n';
	outputTextarea.scrollTop = outputTextarea.scrollHeight;
}

eel.expose(setText);
function setText(text) {
	var outputTextarea = document.getElementById("output");
	outputTextarea.value = text;
	outputTextarea.scrollTop = output.scrollHeight;
}

eel.expose(updateProgressBar);
function updateProgressBar(i, total) {
	const progressBar = document.getElementById('progressBar');
	const percentageCounter = document.getElementById('percentageCounter');

	const progressValue = i / total * 100;

	progressBar.value = progressValue;
	percentageCounter.textContent = `${i} / ${total} (${progressValue.toFixed(0)}%)`;
}

eel.expose(showAlert);
function showAlert(alertText) {
	alert(alertText);
}