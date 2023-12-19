# Praktika-kafedra-fonetiki-2023

## Requirements
Для работы python файла необходимо установить некоторые библиотеки используя следующую команду:
```python
$ pip install -r requirements.txt
```

Так же вам понадобится установить FFmpeg, следуйте инструкциям для вашей операционной системы https://www.ffmpeg.org/download.html

## Порядок работы
Первым делом запустите скрипт для объединения видео:
- combine.ps1 если вы используюте Windows
- сombine.sh если вы используете Linux или MacOS

Скрипт создаст папки WAV и VID в папке с видео файлами. В них будут объединённые звуковой и видео файлы соответственно, С0000.WAV и С0000.MP4

Побочные файлы, необходимые для работы скрипта, можно удалить.

Обратите внимание, что из-за размера видео файлов вам понадобится свободная память 3x от объёма изначальных файлов.
Это необходимо для сохранения качества видео. Если вам нужно уменьшить качество и размер получившегося файла примените следующую команду
```shell
ffmpeg -i C0000.MP4 -b:v N output.MP4
```
N - битрейт конечного результата, минимум 2000k

После завершения работы скрипта переместите звуковой и видео файлы в одну папку и запустите python скрипт
