# Merit Mantra portable pipeline - one-click installer / checker.
#   INSTALL.cmd      -> installs what is missing, signs in, saves your Sarvam key
#   CHECK_SETUP.cmd  -> same checks with -CheckOnly: reports only, changes nothing
param([switch]$CheckOnly)
$ErrorActionPreference = 'Continue'
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$HF = 'hyperframes@0.9.5'
$problems = @()

function Say($msg, $color = 'White') { Write-Host $msg -ForegroundColor $color }
function Ok($msg) { Say "  [OK]   $msg" 'Green' }
function Bad($msg) { Say "  [MISSING] $msg" 'Yellow'; $script:problems += $msg }
function Refresh-Path {
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
}
function Has($cmd) { return [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }
function Winget-Install($id, $name) {
    if ($CheckOnly) { return }
    if (-not (Has 'winget')) {
        Say "  winget is not available. Install '$name' by hand (see GUIDE.md, section 'Manual install'), then run INSTALL.cmd again." 'Red'
        return
    }
    Say "  Installing $name ..." 'Cyan'
    winget install --id $id -e --silent --accept-package-agreements --accept-source-agreements
    Refresh-Path
}

Say ''
Say '=== Merit Mantra video pipeline - setup ===' 'Cyan'
Say "Folder: $Root"
if ($CheckOnly) { Say '(check only - nothing will be installed or changed)' 'DarkGray' }
Say ''

# 1. Python 3.12
Say '1. Python 3.12'
$py = $false
if (Has 'py') { & py -3.12 --version *> $null; $py = ($LASTEXITCODE -eq 0) }
if (-not $py) { Winget-Install 'Python.Python.3.12' 'Python 3.12'; if (Has 'py') { & py -3.12 --version *> $null; $py = ($LASTEXITCODE -eq 0) } }
if ($py) { Ok ((& py -3.12 --version) -join ' ') } else { Bad 'Python 3.12 (py -3.12)' }

# 2. Node.js
Say '2. Node.js'
if (-not (Has 'node')) { Winget-Install 'OpenJS.NodeJS.LTS' 'Node.js LTS' }
if (Has 'node') { Ok ("Node " + (& node --version)) } else { Bad 'Node.js' }

# 3. FFmpeg
Say '3. FFmpeg'
if (-not (Has 'ffmpeg')) { Winget-Install 'Gyan.FFmpeg' 'FFmpeg' }
if (Has 'ffmpeg') { Ok ((& ffmpeg -version | Select-Object -First 1) -replace ' Copyright.*', '') } else { Bad 'FFmpeg (open a new window after installing so PATH updates)' }

# 4. Python packages
Say '4. Python packages (sarvamai, numpy, pillow, httpx)'
if ($py) {
    if (-not $CheckOnly) { & py -3.12 -m pip install --disable-pip-version-check -q -r "$Root\setup\requirements.txt" }
    & py -3.12 -c "import sarvamai, numpy, PIL, httpx" *> $null
    if ($LASTEXITCODE -eq 0) { Ok 'all imported' } else { Bad 'Python packages (run INSTALL.cmd)' }
}

# 5. HyperFrames CLI + render browser
Say "5. HyperFrames CLI ($HF) and its Chrome"
if (Has 'npx') {
    if (-not $CheckOnly) {
        & npm install --no-audit --no-fund --loglevel=error *> $null
        & npx --yes $HF browser ensure
    }
    $v = (& npx --yes $HF --version 2>$null | Select-Object -Last 1)
    if ($LASTEXITCODE -eq 0 -and $v) { Ok "hyperframes $v" } else { Bad 'HyperFrames CLI' }
    $bp = (& npx --yes $HF browser path 2>$null | Select-Object -Last 1)
    if ($bp -and (Test-Path $bp)) { Ok "render browser: $bp" } else { Bad 'Render browser (run INSTALL.cmd)' }
} else { Bad 'npx (comes with Node.js)' }

# 6. HeyGen sign-in (free account) for the free stock-image search
Say '6. HeyGen sign-in (free account, used for free stock images)'
if (Has 'npx') {
    $st = (& npx --yes $HF auth status 2>&1) -join "`n"
    if ($st -notmatch 'valid' -and -not $CheckOnly) {
        Say '  A browser window will open: sign in (or sign up free) at HeyGen, then come back here.' 'Cyan'
        & npx --yes $HF auth login
        $st = (& npx --yes $HF auth status 2>&1) -join "`n"
    }
    if ($st -match 'Account:\s*(\S+)') { Ok "signed in as $($Matches[1])" } else { Bad 'HeyGen sign-in (run INSTALL.cmd)' }
}

# 7. Sarvam API key (voice + optional script writer), stored in .env next to this guide - never printed
Say '7. Sarvam API key'
$envFile = Join-Path $Root '.env'
$hasKey = (Test-Path $envFile) -and ((Get-Content $envFile -ErrorAction SilentlyContinue) -match '^\s*SARVAM_API_KEY\s*=\s*\S+')
if (-not $hasKey -and -not $CheckOnly) {
    Say '  Get your key at https://dashboard.sarvam.ai (API keys). New accounts get free credits.' 'Cyan'
    $sec = Read-Host '  Paste your Sarvam API key (input is hidden) and press Enter' -AsSecureString
    $key = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
    if ($key.Trim()) {
        Set-Content -Path $envFile -Value "SARVAM_API_KEY=$($key.Trim())" -Encoding ASCII
        $hasKey = $true
    }
}
if ($hasKey) { Ok 'key saved in .env' } else { Bad 'Sarvam API key (.env)' }

Say ''
if ($problems.Count -eq 0) {
    Say 'All set. Next: put a topic in the inbox folder and double-click MAKE_VIDEO.cmd (see GUIDE.md).' 'Green'
} else {
    Say 'Still missing:' 'Yellow'
    $problems | ForEach-Object { Say "  - $_" 'Yellow' }
    if (-not $CheckOnly) { Say 'Close this window, open a NEW one and run INSTALL.cmd again (new installs need a fresh window).' 'Yellow' }
}
