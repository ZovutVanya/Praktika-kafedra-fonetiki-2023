#!/bin/bash

# Set the input directory
echo -n "Enter the directory with videos: "
read inputDirectory

# Create output folder for resampled .MP4 files
vidFolder="$inputDirectory/VID"
mkdir -p "$vidFolder"

# Create output folder for WAV files
wavFolder="$inputDirectory/WAV"
mkdir -p "$wavFolder"

# Iterate through each file in the input directory
for file in "$inputDirectory"/*.MP4; do
    # Check if any files match the pattern
    if [ -e "$file" ]; then
        # Generate the output wav path
        outputWavFile="$wavFolder/$(basename "${file%.*}").WAV"
        # Build and execute the FFmpeg command
        ffmpeg -i "$file" -map 0:a:0 "$outputWavFile"

        # Generate the output video path
        outputMP4Path="$vidFolder/$(basename "$file")"
        # Build and execute the FFmpeg command
        ffmpeg -i "$file" -c:v copy -c:a flac "$outputMP4Path"
    fi
done

# Generate the concatenated wav path
outputConcatenatedWav="$wavFolder/C0000.WAV"

# create list with wavs to concat
outputTxtFileWAV="$wavFolder/mylist.txt"

# generate a list of wavs
wavFiles=("$wavFolder"/*.WAV)

# Create a list of file entries
for wavFile in "${wavFiles[@]}"; do
    echo "file '$wavFile'" >> "$outputTxtFileWAV"
done

# Build and execute the FFmpeg command
ffmpeg -f concat -safe 0 -i "$outputTxtFileWAV" -c copy "$outputConcatenatedWav"

# Generate the concatenated video path
outputConcatenatedMP4="$vidFolder/C0000.MP4"

# create list with vids to concat
outputTxtFileMP4="$vidFolder/mylist.txt"

# generate a list of vids
mp4Files=("$vidFolder"/*.MP4)

# Create a list of file entries
for mp4File in "${mp4Files[@]}"; do
    echo "file '$mp4File'" >> "$outputTxtFileMP4"
done

# Build and execute the FFmpeg command
ffmpeg -f concat -safe 0 -i "$outputTxtFileMP4" -c copy "$outputConcatenatedMP4"
