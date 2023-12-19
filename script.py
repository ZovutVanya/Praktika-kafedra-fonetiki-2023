import os
import tgt
import librosa

import numpy as np
import numpy.typing as npt

from time import time
from scipy import signal
from datetime import timedelta
from colorama import Fore, init
from chardet.universaldetector import UniversalDetector


def find_encoding(path: str) -> str:
    detector = UniversalDetector()
    with open(path, "rb") as fh:
        for line in fh:
            detector.feed(line)
            if detector.done:
                break
        detector.close()
    return detector.result["encoding"]


init()
SAMPLING_RATE = 48000


def preprocess_audio(
    path: str, sampling_rate=SAMPLING_RATE
) -> tuple[npt.NDArray[np.float64], str]:
    filename, _ = os.path.splitext(path)
    y, sr = librosa.load(path)
    y_mono = librosa.to_mono(y)
    y_resampled = librosa.resample(y_mono, orig_sr=sr, target_sr=sampling_rate)

    return y_resampled, filename


def read_txt(path: str) -> list[str]:
    with open(path, "r") as reader:
        res = reader.readlines()
    return res


def fix_textgrid(lines: list[str]) -> list[str]:
    broken_line_start, broken_line_end = -1, -1
    broken_lines = []

    for i, line in enumerate(lines):
        if "text" in line and line.count('"') == 1:
            broken_line_start = i

        elif line.count('"') == 1 and broken_line_start != -1:
            broken_line_end = i

        if broken_line_start != -1 and broken_line_end != -1:
            broken_lines.append([broken_line_start, broken_line_end])
            broken_line_start, broken_line_end = -1, -1

    for lines_tuple in broken_lines:
        lines[lines_tuple[0]] = (
            " ".join(
                [i.replace("\n", "") for i in lines[lines_tuple[0] : lines_tuple[1]]]
            )
            + '"'
        )
        [lines.pop(i) for i in range(lines_tuple[1], lines_tuple[0], -1)]

    return lines


def write_txt(path: str, lines: list[str]) -> None:
    with open(path, "w") as writer:
        writer.writelines(lines)


def read_tgt(path: str) -> dict[str, tgt.core.Interval]:
    try:
        tg = tgt.io.read_textgrid(path, encoding=find_encoding(path))
    except Exception:
        lines = read_txt(path)
        new_lines = fix_textgrid(lines)
        write_txt(path, new_lines)
        tg = tgt.io.read_textgrid(path, encoding=find_encoding(path))
    res = {}
    for name in tg.get_tier_names():
        res[name] = tg.get_tier_by_name(name)._objects[0]
    return res


def write_srt(
    unsorted_data: dict[str, tuple[float, float]],
    filename: str,
    tgt_path: str,
    srt_name="",
) -> None:
    # сортируем по начальной временной метке
    sorted_data = {
        k: v for k, v in sorted(unsorted_data.items(), key=lambda x: x[1][0])
    }

    filename, _ = os.path.splitext(filename)

    id_num = 0
    srtFilename = f"{filename}[{srt_name}].srt"
    files = os.listdir(tgt_path)
    tg_dict = {}

    for file in files:
        if file.endswith(".TextGrid"):
            key = os.path.splitext(os.path.basename(file))[0]

            try:
                tg_intervals = read_tgt(tgt_path + os.sep + file)
                tg_dict[key] = tg_intervals

            except Exception as e:
                print(e)

    with open(srtFilename, "w", encoding="utf-8") as srtFile:
        for key, start_end in sorted_data.items():
            # write labels
            id_num += 1
            startTime = str(timedelta(seconds=start_end[0])).replace(".", ",")[:-3]
            endTime = str(timedelta(seconds=start_end[1])).replace(".", ",")[:-3]

            if len(startTime.strip(":")[0]) == 1:
                startTime = str(0) + startTime

            if len(endTime.strip(":")[0]) == 1:
                endTime = str(0) + endTime

            text = key.strip()
            segmentId = id_num
            segment = f"{segmentId}\n{startTime} --> {endTime}\n{{\\an9}}{text}\n\n"

            srtFile.write(segment)

            # write context
            if key in tg_dict.keys():
                id_num += 1
                startTime = str(timedelta(seconds=start_end[0])).replace(".", ",")[:-3]
                endTime = str(timedelta(seconds=start_end[1])).replace(".", ",")[:-3]

                if len(startTime.strip(":")[0]) == 1:
                    startTime = str(0) + startTime

                if len(endTime.strip(":")[0]) == 1:
                    endTime = str(0) + endTime

                text = tg_dict[key]["c"].text.strip()
                segmentId = id_num
                segment = f"{segmentId}\n{startTime} --> {endTime}\n{{\\an1}}{text}\n\n"

                srtFile.write(segment)

                # write aim
                id_num += 1
                startTime = str(
                    timedelta(seconds=start_end[0] + tg_dict[key]["s"].start_time)
                ).replace(".", ",")[:-3]
                endTime = str(
                    timedelta(seconds=start_end[0] + tg_dict[key]["s"].end_time)
                ).replace(".", ",")[:-3]

                if len(startTime.strip(":")[0]) == 1:
                    startTime = str(0) + startTime

                if len(endTime.strip(":")[0]) == 1:
                    endTime = str(0) + endTime

                text = tg_dict[key]["s"].text.strip()
                segmentId = id_num
                segment = f"{segmentId}\n{startTime} --> {endTime}\n{{\\an7}}{text}\n\n"

                srtFile.write(segment)


def find_offset(
    within_file: str,
    video_path: str,
    find_file_directory: str,
    srt_name: str,
    sr=SAMPLING_RATE,
) -> None:
    y_within, _ = preprocess_audio(within_file)

    if os.path.exists(find_file_directory):
        print(Fore.CYAN + "[~] Сканирование директории контекстов")
        audio_in_dir = os.listdir(find_file_directory)

        data_for_subtitles = {}
        audio_files_to_find = {}
        print(Fore.CYAN + "[~] Предобработка аудио контекстов")

        k = 0
        for file in audio_in_dir:
            if file.endswith(".wav") or file.endswith(".WAV"):
                filename, _ = os.path.splitext(file)
                try:
                    y_find, _ = preprocess_audio(find_file_directory + os.sep + file)
                except Exception as e:
                    print(e)
                    continue

                audio_files_to_find[filename] = y_find
                k += 1
                print(
                    Fore.GREEN
                    + "[+] Выполнено "
                    + str(round(k * 2 * 100 / len(audio_in_dir), 2))
                    + "%"
                )

        if len(audio_files_to_find) > 0:
            print(Fore.CYAN + "[~] Запись субтитров")
            k = 0
            for key, y_find in audio_files_to_find.items():
                c = signal.correlate(y_within, y_find, mode="valid", method="fft")
                peak = np.argmax(c)
                offset = round(peak / sr, 4)
                end_offset = round((peak + len(y_find)) / sr, 4)
                data_for_subtitles[key] = (offset, end_offset)
                k += 1
                print(
                    Fore.GREEN
                    + "[+] Выполнено "
                    + str(round(k * 100 / len(audio_files_to_find), 2))
                    + "%"
                )

            write_srt(data_for_subtitles, video_path, find_file_directory, srt_name)
            print(Fore.GREEN + "[+] Субтитры записаны")
    else:
        print(Fore.RED + "[-] Директория контекстов не найдена")


if __name__ == "__main__":
    speaker = input("Путь к папке с видео: ")
    path_to_contexts = input("Путь к папке контекстов: ")
    srt_name = input("Название для файла субтитров (пример - фразы5): ")

    start_time = time()

    video_path = os.path.join(speaker, "C0000.MP4")

    audio_path = os.path.join(speaker, "C0000.WAV")

    find_offset(audio_path, video_path, path_to_contexts, srt_name)

    print(Fore.MAGENTA + f"~~~~~~ Finished in: {time() - start_time:.2f}s ~~~~~~")
