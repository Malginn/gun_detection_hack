// Функция для отображения информации и предпросмотра файла
function displayFileInfo() {
    var fileInput = document.getElementById('fileInput');
    var file = fileInput.files[0]; // Получаем выбранный файл

    if (file) {
        // Отображение параметров файла
        var fileExtension = file.name.split('.').pop().toLowerCase();
        var imageInfo = document.getElementById('imageInfo');

        if (fileExtension === 'jpg' || fileExtension === 'jpeg' || fileExtension === 'png' || fileExtension === 'gif') {
            // Если файл - изображение
            imageInfo.innerHTML = 'Имя файла: ' + file.name + '<br>' +
                'Тип файла: ' + file.type + '<br>' +
                'Размер файла: ' + (file.size / 1024).toFixed(2) + ' KB';

            // Отображаем элементы для изображения
            var imagePreview = document.getElementById('imagePreview');
            imagePreview.style.display = 'block';

            var volume = document.getElementById('volume');
            volume.style.display = 'none';

            var videoPlayer = document.getElementById('videoPlayer');
            videoPlayer.style.display = 'none';

            // Создаем URL для предпросмотра выбранной картинки
            var imageUrl = URL.createObjectURL(file);
            var previewImage = document.getElementById('previewImage');
            previewImage.style.display = 'inline-block';
            previewImage.src = imageUrl;
        } else if (fileExtension === 'mp4') {
            // Если файл - видео
            imageInfo.innerHTML = 'Имя файла: ' + file.name + '<br>' +
                'Тип файла: ' + file.type + '<br>' +
                'Размер файла: ' + (file.size / 1024).toFixed(2) + ' KB';

            // Отображаем элементы для видео
            var imagePreview = document.getElementById('imagePreview');
            imagePreview.style.display = 'block';

            var volume = document.getElementById('volume');
            volume.style.display = 'none';

            var previewImage = document.getElementById('previewImage');
            previewImage.style.display = 'none';

            var videoPlayer = document.getElementById('videoPlayer');
            videoPlayer.style.display = 'block';

            videoPlayer.src = URL.createObjectURL(file);
        } else {
            imageInfo.innerHTML = 'Неизвестный тип файла';
        }
    } else {
        // Если файл не выбран, очищаем информацию и предпросмотр
        var imageInfo = document.getElementById('imageInfo');
        imageInfo.innerHTML = '';
        var imagePreview = document.getElementById('imagePreview');
        imagePreview.src = '';
        var previewImage = document.getElementById('previewImage');
        previewImage.src = '';
        var imagePreview = document.getElementById('imagePreview');
        imagePreview.style.display = 'none';
        var volume = document.getElementById('volume');
        volume.style.display = 'none';
    }
}

// Обработчик события изменения файла
document.getElementById('fileInput').addEventListener('change', displayFileInfo);

// Функция для отправки файла на сервер с использованием Fetch API
function uploadFile() {
    var fileInput = document.getElementById('fileInput');
    var file = fileInput.files[0]; // Получаем выбранный файл

    if (file) {
        var formData = new FormData(); // Создаем объект FormData для отправки файла на сервер
        formData.append('file', file); // Добавляем файл в FormData

        // Опции для запроса
        var options = {
            method: 'PUT',
            body: formData
        };
        showLoadingIndicator()
        // Выполняем запрос к серверу
        fetch('http://localhost:8000/api/nn/', options)
            .then(response => response.json())
            .then(data => {
                
                check(data['task_key'])
            })
            .catch(error => {
                console.error('Ошибка:', error);
            });
    } else {
        alert('Пожалуйста, выберите файл для загрузки.');
    }
}


function check (task) {
var options = {
    method: 'GET'
};
fetch('http://localhost:8000/api/task/?task_key='+task, options)
.then(data => {
    //console.log(data.works)
    

var volume = document.getElementById('volume');
volume.style.display = 'block';
// Скрываем индикатор загрузки
    // Скрываем индикатор загрузки
            if (data['status'] !== 'done') {
        
                setTimeout(function () {
                    check(task);
                }, 5000); // 5000 миллисекунд = 5 секунд
            } else {
                hideLoadingIndicator();
            }

})
.catch(error => {
console.error('Ошибка:', error);
// Скрываем индикатор загрузки
hideLoadingIndicator();
});
                }

function animateNumber(number) {
    var volumeH = document.querySelector('#volume h1');
    volumeH.textContent = number + ' m³';
}

// Функция для отображения индикатора загрузки
function showLoadingIndicator() {
    var loadingIndicator = document.getElementById('loadingIndicator');
    loadingIndicator.style.display = 'block';
}

// Функция для скрытия индикатора загрузки
function hideLoadingIndicator() {
    var loadingIndicator = document.getElementById('loadingIndicator');
    loadingIndicator.style.display = 'none';
}