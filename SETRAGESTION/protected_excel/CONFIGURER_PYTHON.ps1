# Script de configuration automatique de l'environnement Python
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Configuration Python pour VS Code" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$pythonPath = Join-Path $PSScriptRoot "python311\python.exe"
$vscodePath = Join-Path $PSScriptRoot ".vscode"
$settingsPath = Join-Path $vscodePath "settings.json"

# Vérifier que Python existe
if (-not (Test-Path $pythonPath)) {
    Write-Host "[ERREUR] Python non trouvé à: $pythonPath" -ForegroundColor Red
    Write-Host "Veuillez installer Python 3.11 dans le dossier python311" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "[OK] Python trouvé: $pythonPath" -ForegroundColor Green

# Vérifier les packages
Write-Host ""
Write-Host "Vérification des packages Python..." -ForegroundColor Yellow
& $pythonPath -c "import streamlit, pandas, plotly, reportlab, PIL, cloudinary, matplotlib, openpyxl" 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "[OK] Tous les packages sont installés" -ForegroundColor Green
} else {
    Write-Host "[ATTENTION] Certains packages manquent" -ForegroundColor Yellow
    Write-Host "Installation des dépendances..." -ForegroundColor Yellow
    & $pythonPath -m pip install -r requirements.txt --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] Packages installés avec succès" -ForegroundColor Green
    } else {
        Write-Host "[ERREUR] Échec de l'installation des packages" -ForegroundColor Red
    }
}

# Afficher le chemin Python pour VS Code
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Configuration VS Code" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pour configurer VS Code manuellement:" -ForegroundColor Yellow
Write-Host "1. Appuyez sur Ctrl+Shift+P" -ForegroundColor White
Write-Host "2. Tapez: Python: Select Interpreter" -ForegroundColor White
Write-Host "3. Sélectionnez ou entrez: .\python311\python.exe" -ForegroundColor White
Write-Host ""
Write-Host "Chemin complet: $pythonPath" -ForegroundColor Cyan
Write-Host ""

# Vérifier la configuration
if (Test-Path $settingsPath) {
    $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json
    $configuredPath = $settings.'python.defaultInterpreterPath'
    
    if ($configuredPath -like "*python311*") {
        Write-Host "[OK] VS Code est configuré pour utiliser python311" -ForegroundColor Green
    } else {
        Write-Host "[ATTENTION] VS Code utilise: $configuredPath" -ForegroundColor Yellow
        Write-Host "Configuration recommandée: .\python311\python.exe" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Actions recommandées" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Rechargez VS Code:" -ForegroundColor Yellow
Write-Host "   Ctrl+Shift+P > Developer: Reload Window" -ForegroundColor White
Write-Host ""
Write-Host "2. Vérifiez l'interpréteur Python:" -ForegroundColor Yellow
Write-Host "   Ctrl+Shift+P > Python: Select Interpreter" -ForegroundColor White
Write-Host ""
Write-Host "3. Redémarrez Pylance:" -ForegroundColor Yellow
Write-Host "   Ctrl+Shift+P > Pylance: Restart Server" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

pause
