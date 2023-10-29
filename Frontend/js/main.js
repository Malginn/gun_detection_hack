// Функция для отображения информации и предпросмотра файла
function displayFileInfo() {
    var fileInput = document.getElementById('fileInput');
    var file = fileInput.files[0]; // Получаем выбранный файл

    document.getElementById('default').style.display = 'none';
    document.getElementById('control').style.display = 'block';
    document.getElementById('test').style.display = 'flex';

    if (file) {
        // Отображение параметров файла
        var fileExtension = file.name.split('.').pop().toLowerCase();
        if (fileExtension === 'jpg' || fileExtension === 'jpeg' || fileExtension === 'png') {
            console.log( 'Имя файла: ' + file.name + ' | ' +
                'Тип файла: ' + file.type + ' | ' +
                'Размер файла: ' + (file.size / 1024).toFixed(2) + ' KB' )
                // Создаем URL для предпросмотра выбранной картинки
                var preview = document.getElementById('preview');
                preview.innerHTML = '<img src="'+URL.createObjectURL(file)+'" width="100%">';
                uploadFile();
        } else if (fileExtension === 'mp4') {
            console.log( 'Имя файла: ' + file.name + ' | ' +
                'Тип файла: ' + file.type + ' | ' +
                'Размер файла: ' + (file.size / 1024).toFixed(2) + ' KB' )
                // Создаем URL для предпросмотра выбранной картинки
                var preview = document.getElementById('preview');
                preview.innerHTML = '<video  src="'+URL.createObjectURL(file)+'" width="100%" controls autoplay></video>';
                uploadFile();
        }
        else if (fileExtension === 'zip') {
            console.log( 'Имя файла: ' + file.name + ' | ' +
                'Тип файла: ' + file.type + ' | ' +
                'Размер файла: ' + (file.size / 1024).toFixed(2) + ' KB' )
                // // Создаем URL для предпросмотра выбранной картинки
                // var preview = document.getElementById('preview');
                // preview.innerHTML = '<video  src="'+URL.createObjectURL(file)+'" width="80%" controls autoplay></video>';
                uploadFile();
        } else {
            console.log( 'Неизвестный тип файла' )
        }
    } else {
        var videoPlayer = document.getElementById('videoPlayer');
        videoPlayer.src = '';
        var previewImage = document.getElementById('previewImage');
        previewImage.src = '';
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
        var fileExtension = file.name.split('.').pop().toLowerCase();
        if(fileExtension === 'zip')
        {
            // Выполняем запрос к серверу
            fetch('http://62.64.112.66:8000/api/archive/', options)
                .then(response => response.json())
                .then(data => {
                    check(data['redis_key'])
                })
                .catch(error => {
                    console.error('Ошибка:', error);
                });
        }
        else
        {
            // Выполняем запрос к серверу
            fetch('http://62.64.112.66:8000/api/nn/', options)
                .then(response => response.json())
                .then(data => {
                    check(data['redis_key'])
                })
                .catch(error => {
                    console.error('Ошибка:', error);
                });
        }
    } else {
        alert('Пожалуйста, выберите файл для загрузки.');
    }
}


function check (task) {
    var options = {
        method: 'GET'
    };
    fetch('http://62.64.112.66:8000/api/task/?task_key='+task, options)
        .then(response => response.json())
        .then(data => {
            console.log(data['status'])
            if (data['status'] !== 'done') {
                setTimeout(function () {
                    check(task);
                }, 5000); // 5000 миллисекунд = 5 секунд
            } else {
                hideLoadingIndicator();

                // Convert single quotes to double quotes to make it valid JSON
                var validJsonString = data.work.replace(/'/g, '"');

                // Parse the valid JSON
                var workArray = JSON.parse(validJsonString);

                console.log(workArray);
                
                var filename =workArray[0];
                //preview.innerHTML = '<img src="http://localhost:8000/api/media/?task_key='+task+'" width="80%">';
                // Проверяем расширение файла
                if (filename.match(/\.(mp4)$/)) {
                    console.log('video')
                    preview.innerHTML = '<video src="http://62.64.112.66:8000/api/video/?task_key='+task+'" width="80%" controls autoplay></video>';
                } else if (filename.match(/\.(jpg|jpeg|png)$/)) {
                    console.log('file')
                    preview.innerHTML = '<img src="http://62.64.112.66:8000/api/media/?task_key='+task+'" style="width: 100%; border-radius: 13px;">';
                }
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            hideLoadingIndicator();
        });
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