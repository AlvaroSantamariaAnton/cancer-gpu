# Cargar en la terminal actual: . .\scripts\activar_casa.ps1
$ErrorActionPreference = 'Stop'
$condaCommand = Get-Command conda -ErrorAction SilentlyContinue
if ($condaCommand) {
    conda activate cancer
} else {
    $condaCandidates = @(
        'D:\proyectos\_herramientas\miniconda3\Scripts\conda.exe',
        "$env:USERPROFILE\miniconda3\Scripts\conda.exe",
        "$env:USERPROFILE\miniforge3\Scripts\conda.exe",
        "$env:USERPROFILE\anaconda3\Scripts\conda.exe"
    )
    $condaExecutable = $condaCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if (-not $condaExecutable) { throw 'No se localiza Conda. Abre Miniconda Prompt y ejecuta conda activate cancer.' }
    (& $condaExecutable 'shell.powershell' 'hook') | Out-String | Invoke-Expression
    conda activate cancer
}
if ($LASTEXITCODE -ne 0) { throw 'No se pudo activar cancer.' }
python --version
