# Compila el C++, genera las trazas reales, renderiza todas las escenas con Manim
# y las une en un solo video: video/CicloEuleriano.mp4
#   .\ejecutar.ps1            -> 1080p60 (calidad final)
#   .\ejecutar.ps1 -Calidad l -> 480p15 (rapido, para probar)
param(
    [ValidateSet('l', 'm', 'h')]
    [string]$Calidad = 'h',
    [string]$Manim = ''
)

$ErrorActionPreference = 'Stop'
$raiz = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $raiz

$ucrtBin = 'C:\msys64\ucrt64\bin'
if (Test-Path (Join-Path $ucrtBin 'g++.exe')) { $env:Path = "$ucrtBin;$env:Path" }

if (-not $Manim) {
    $candidatos = @(
        (Join-Path $raiz '.venv-manim\Scripts\manim.exe'),
        (Join-Path $raiz '..\suffix-tree-aed\.venv-manim313\Scripts\manim.exe')
    )
    $Manim = ($candidatos | Where-Object { Test-Path $_ } | Select-Object -First 1)
    if (-not $Manim) { $Manim = 'manim' }
}

Write-Host 'Compilando...' -ForegroundColor Cyan
& g++ -std=c++17 -Wall -Wextra -O2 -o euler.exe src/main.cpp src/GrafoEuleriano.cpp
& g++ -std=c++17 -O2 -Isrc -o pruebas.exe tests/pruebas.cpp src/GrafoEuleriano.cpp

Write-Host 'Pruebas...' -ForegroundColor Cyan
& .\pruebas.exe
if ($LASTEXITCODE -ne 0) { throw 'Fallaron las pruebas' }

Write-Host 'Generando trazas reales...' -ForegroundColor Cyan
New-Item -ItemType Directory -Force trazas | Out-Null
foreach ($g in 'principal', 'konigsberg', 'desconectado', 'un_vertice') {
    & .\euler.exe "grafos\$g.txt" -t "trazas\$g.txt"
}

$escenas = 'Portada', 'Introduccion', 'Verificacion', 'Hierholzer', 'CasoBorde', 'Complejidad', 'Creditos'
Write-Host "Renderizando en calidad $Calidad..." -ForegroundColor Cyan
foreach ($e in $escenas) { & $Manim "-q$Calidad" animacion\escena.py $e }

$carpeta = @{ l = '480p15'; m = '720p30'; h = '1080p60' }[$Calidad]
New-Item -ItemType Directory -Force video | Out-Null
$lista = Join-Path $raiz 'video\lista.txt'
$escenas | ForEach-Object { "file '../media/videos/escena/$carpeta/$_.mp4'" } | Set-Content -Encoding ascii $lista
& ffmpeg -y -v error -f concat -safe 0 -i $lista -c copy video\CicloEuleriano.mp4
Remove-Item $lista
Copy-Item "media\videos\escena\$carpeta\*.mp4" video\ -Force
Write-Host 'Listo: video\CicloEuleriano.mp4 (y cada escena por separado en video\)' -ForegroundColor Green
