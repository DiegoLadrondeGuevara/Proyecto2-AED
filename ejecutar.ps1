# Compila el C++, corre las pruebas, genera las trazas reales y renderiza
# cada escena de Manim en la carpeta video/
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
    $local = Join-Path $raiz '.venv-manim\Scripts\manim.exe'
    $Manim = if (Test-Path $local) { $local } else { 'manim' }
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
Copy-Item "media\videos\escena\$carpeta\*.mp4" video\ -Force
Write-Host 'Listo: cada escena esta en la carpeta video\' -ForegroundColor Green
