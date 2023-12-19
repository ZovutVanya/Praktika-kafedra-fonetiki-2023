# Set the input directory
$inputDirectory = Read-Host "Enter the directory with videos"

# Create output folder for resampled .MP4 files
$vidFolder = Join-Path $inputDirectory "VID"
New-Item -ItemType Directory -Force -Path $vidFolder | Out-Null

# Create output folder for WAV files
$wavFolder = Join-Path $inputDirectory "WAV"
New-Item -ItemType Directory -Force -Path $wavFolder | Out-Null

# Iterate through each file in the input directory
Get-ChildItem -Path $inputDirectory -Filter *.MP4 | ForEach-Object {
    # Generate the output wav path
    $outputWavFile = Join-Path $wavFolder ($_.BaseName + ".WAV")
    # Build and execute the FFmpeg command
    & ffmpeg -i $_.FullName -map 0:a:0 $outputWavFile

    # Generate the output video path
    $outputMP4Path = Join-Path $vidFolder $_.Name
    # Build and execute the FFmpeg command
    & ffmpeg -i $_.FullName -c:v copy -c:a flac $outputMP4Path
}

# Generate the concatenated wav path
$outputConcatenatedWav = Join-Path $wavFolder "C0000.WAV"

# create list with wavs to concat
$outputTxtFileWAV = Join-Path $wavFolder "mylist.txt"

# generate a list of wavs
$wavFiles = Get-ChildItem -Path $wavFolder -Filter *.WAV

# Create a list of file entries
$wavFileEntries = $wavFiles | ForEach-Object { "file '$($_.FullName)'" }

# Write the list to the output text file
$wavFileEntries | Out-File -FilePath $outputTxtFileWAV

# Build and execute the FFmpeg command
& ffmpeg -f concat -safe 0 -i $outputTxtFileWAV -c copy $outputConcatenatedWav

############################################################################

# Generate the concatenated video path
$outputConcatenatedMP4 = Join-Path $vidFolder "C0000.MP4"

# create list with vids to concat
$outputTxtFileMP4 = Join-Path $vidFolder "mylist.txt"

# generate a list of wavs
$mp4Files = Get-ChildItem -Path $vidFolder -Filter *.MP4

# Create a list of file entries
$mp4FileEntries = $mp4Files | ForEach-Object { "file '$($_.FullName)'" }

# Write the list to the output text file
$mp4FileEntries | Out-File -FilePath $outputTxtFileMP4

# Build and execute the FFmpeg command
& ffmpeg -f concat -safe 0 -i $outputTxtFileMP4 -c copy $outputConcatenatedMP4