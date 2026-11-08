param(
    [string]$ProjectDir = 'D:/projects/vultre'
)
$ErrorActionPreference = 'Stop'
$videoDir = Join-Path $ProjectDir 'submission/agent-rush/video'
$audioDir = Join-Path $videoDir '.build/audio'
New-Item -ItemType Directory -Path $audioDir -Force | Out-Null
$story = Get-Content -LiteralPath (Join-Path $videoDir 'storyboard.json') -Raw -Encoding utf8 | ConvertFrom-Json
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $synth.SelectVoice($story.voice)
    $synth.Rate = 0
    $synth.Volume = 100
    for ($index = 0; $index -lt $story.scenes.Count; $index++) {
        $audioPath = Join-Path $audioDir ('scene-{0:00}.wav' -f ($index + 1))
        $synth.SetOutputToWaveFile($audioPath)
        $synth.Speak($story.scenes[$index].narration)
        $synth.SetOutputToNull()
        Write-Output ('Narrated scene {0}: {1}' -f ($index + 1), $story.scenes[$index].title)
    }
}
finally {
    $synth.Dispose()
}
