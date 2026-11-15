param(
    [ValidateSet("BuildExe", "RunApp", "VerifyEnvOnly")]
    [string]$Action = "BuildExe",
    [switch]$SkipOllama
)

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

$RuntimeDir = Join-Path $ProjectRoot ".runtime"
$CacheDir = Join-Path $RuntimeDir "cache"
$PipCacheDir = Join-Path $CacheDir "pip"
$PortablePyDir = Join-Path $RuntimeDir "python"
$LocalVenvDir = Join-Path $RuntimeDir "venv"
$PortableOllamaDir = Join-Path $RuntimeDir "ollama"
$PortableModelsDir = Join-Path $RuntimeDir "ollama_models"

New-Item -ItemType Directory -Force -Path $RuntimeDir, $CacheDir, $PipCacheDir | Out-Null
$env:PIP_CACHE_DIR = $PipCacheDir
$env:PIP_DISABLE_PIP_VERSION_CHECK = "1"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  ALTAR-NASA v6.3 : Flame in Freefall - Portable Setup & Launcher" -ForegroundColor Cyan
Write-Host "  Project Folder  : $ProjectRoot" -ForegroundColor Gray
Write-Host "  Action Mode     : $Action" -ForegroundColor Gray
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

# 0. Unblock Mark-of-the-Web (Zone.Identifier) on extracted GitHub ZIP files
try {
    Get-ChildItem -Path $ProjectRoot -Recurse -File -ErrorAction SilentlyContinue | Unblock-File -ErrorAction SilentlyContinue
} catch {}

function Write-Utf8NoBom {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string]$Text
    )
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    [System.IO.File]::WriteAllText($FilePath, $Text, $utf8NoBom)
}

function Invoke-NativeCommand {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [string[]]$Arguments = @(),
        [switch]$Quiet
    )
    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        $global:LASTEXITCODE = 0
        if ($Quiet) {
            $null = & $FilePath @Arguments 2>&1
        } else {
            & $FilePath @Arguments | Out-Host
        }
        if ($null -eq $LASTEXITCODE) { return 0 }
        return [int]$LASTEXITCODE
    } catch {
        return 1
    } finally {
        $ErrorActionPreference = $prevEap
    }
}

function Download-FileFast {
    param(
        [Parameter(Mandatory = $true)][string]$Url,
        [Parameter(Mandatory = $true)][string]$OutFile,
        [string]$Label = "Package"
    )
    if (Test-Path $OutFile) {
        Remove-Item -Force $OutFile -ErrorAction SilentlyContinue
    }
    Write-Host "[DOWNLOAD] Fetching $Label..." -ForegroundColor Yellow
    Write-Host "           Source: $Url" -ForegroundColor DarkGray
    $req = [System.Net.HttpWebRequest]::Create($Url)
    $req.UserAgent = "ALTAR-NASA-Installer/6.3"
    $req.AllowAutoRedirect = $true
    $req.Timeout = 30000
    $req.ReadWriteTimeout = 60000
    $resp = $req.GetResponse()
    try {
        $totalBytes = $resp.ContentLength
        $inStream = $resp.GetResponseStream()
        $outStream = New-Object System.IO.FileStream($OutFile, [System.IO.FileMode]::Create, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None, 65536)
        try {
            $buffer = New-Object byte[] 65536
            $readTotal = [long]0
            $sw = [System.Diagnostics.Stopwatch]::StartNew()
            $lastLogMs = -2000
            while (($read = $inStream.Read($buffer, 0, $buffer.Length)) -gt 0) {
                $outStream.Write($buffer, 0, $read)
                $readTotal += $read
                if (($sw.ElapsedMilliseconds - $lastLogMs) -ge 2000) {
                    $lastLogMs = $sw.ElapsedMilliseconds
                    $mbDone = [math]::Round($readTotal / 1MB, 1)
                    if ($totalBytes -gt 0) {
                        $mbTotal = [math]::Round($totalBytes / 1MB, 1)
                        $pct = [math]::Round(($readTotal * 100.0) / $totalBytes, 1)
                        Write-Host ("           Progress: {0} / {1} MB ({2}%)" -f $mbDone, $mbTotal, $pct) -ForegroundColor DarkCyan
                    } else {
                        Write-Host ("           Progress: {0} MB downloaded..." -f $mbDone) -ForegroundColor DarkCyan
                    }
                }
            }
        } finally {
            $outStream.Close()
            $inStream.Close()
        }
    } finally {
        $resp.Close()
    }
    $finalMb = [math]::Round((Get-Item $OutFile).Length / 1MB, 1)
    Write-Host "[OK] $Label completed ($finalMb MB)." -ForegroundColor Green
}

function Test-PythonInterpreter {
    param(
        [string]$ExePath,
        [string[]]$PrefixArgs = @(),
        [switch]$AllowNoTk
    )
    if (-not $ExePath) { return $false }
    if (($ExePath -match "WindowsApps") -and (-not (Test-Path $ExePath))) { return $false }
    $probePy = Join-Path $CacheDir "probe_py.py"
    if (-not (Test-Path $probePy)) {
        $pyCode = @"
import sys, venv, ssl
if sys.version_info < (3, 10):
    sys.exit(1)
if "--allow-no-tk" not in sys.argv:
    import tkinter as _tk
    _tk.Tcl()
sys.exit(0)
"@
        Write-Utf8NoBom -FilePath $probePy -Text $pyCode
    }
    $argsList = @() + $PrefixArgs + @($probePy)
    if ($AllowNoTk) {
        $argsList += "--allow-no-tk"
    }
    $code = Invoke-NativeCommand -FilePath $ExePath -Arguments $argsList -Quiet
    return ($code -eq 0)
}

function Test-AllRequiredPackages {
    param([string]$PyExe)
    if (-not $PyExe -or -not (Test-Path $PyExe)) { return $false }
    $probePkg = Join-Path $CacheDir "probe_pkg.py"
    if (-not (Test-Path $probePkg)) {
        $pkgCode = @"
import sys, flask, werkzeug, requests, certifi, bs4, numpy, fitz, dotenv, PIL, PyInstaller
sys.exit(0)
"@
        Write-Utf8NoBom -FilePath $probePkg -Text $pkgCode
    }
    $code = Invoke-NativeCommand -FilePath $PyExe -Arguments @($probePkg) -Quiet
    return ($code -eq 0)
}

function Ensure-VcRedistIfMissing {
    $sys32 = Join-Path $env:SystemRoot "System32"
    $hasMsvcp = Test-Path (Join-Path $sys32 "msvcp140.dll")
    $hasVcRun1 = Test-Path (Join-Path $sys32 "vcruntime140_1.dll")
    if ($hasMsvcp -and $hasVcRun1) {
        return
    }
    Write-Host "[SETUP] Missing Microsoft Visual C++ 2015-2022 Runtime (x64) detected; downloading..." -ForegroundColor Yellow
    $vcExe = Join-Path $CacheDir "vc_redist.x64.exe"
    try {
        Download-FileFast -Url "https://aka.ms/vs/17/release/vc_redist.x64.exe" -OutFile $vcExe -Label "Microsoft VC++ Redistributable x64"
        $vcProc = Start-Process -FilePath $vcExe -ArgumentList "/install /quiet /norestart" -Wait -PassThru
        Remove-Item -Force $vcExe -ErrorAction SilentlyContinue
        if ($vcProc.ExitCode -eq 0 -or $vcProc.ExitCode -eq 3010 -or $vcProc.ExitCode -eq 1638) {
            Write-Host "[OK] Microsoft VC++ Runtime ready." -ForegroundColor Green
        } else {
            Write-Host "[INFO] VC++ installer exit code: $($vcProc.ExitCode) (continuing with bundled local DLLs)." -ForegroundColor DarkGray
        }
    } catch {
        Write-Host "[INFO] VC++ Runtime installation skipped: $($_.Exception.Message)" -ForegroundColor DarkGray
    }
}

function Install-PortablePythonToRuntime {
    New-Item -ItemType Directory -Force -Path $PortablePyDir | Out-Null
    $portablePyExe = Join-Path $PortablePyDir "python.exe"

    # Primary method: Zero-Registry official PSF NuGet Python 3.12.8 + Tcl/Tk bundle
    try {
        $nupkgZip = Join-Path $CacheDir "python-3.12.8.nupkg.zip"
        Download-FileFast -Url "https://api.nuget.org/v3-flatcontainer/python/3.12.8/python.3.12.8.nupkg" -OutFile $nupkgZip -Label "Official Portable Python 3.12.8 (x64)"
        $nupkgExtract = Join-Path $CacheDir "py_nupkg_ext"
        if (Test-Path $nupkgExtract) { Remove-Item -Recurse -Force $nupkgExtract }
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        [System.IO.Compression.ZipFile]::ExtractToDirectory($nupkgZip, $nupkgExtract)
        Copy-Item -Path (Join-Path $nupkgExtract "tools\*") -Destination $PortablePyDir -Recurse -Force
        Remove-Item -Recurse -Force $nupkgExtract, $nupkgZip -ErrorAction SilentlyContinue

        try {
            $tcltkMsi = Join-Path $CacheDir "tcltk-3.12.8.msi"
            $tcltkAdm = Join-Path $CacheDir "tcltk_adm"
            if (Test-Path $tcltkAdm) { Remove-Item -Recurse -Force $tcltkAdm }
            Download-FileFast -Url "https://www.python.org/ftp/python/3.12.8/amd64/tcltk.msi" -OutFile $tcltkMsi -Label "Official Python Tcl/Tk 8.6 GUI Runtime"
            $msiProc = Start-Process -FilePath "msiexec.exe" -ArgumentList @("/a", "`"$tcltkMsi`"", "/qn", "TARGETDIR=`"$tcltkAdm`"") -Wait -PassThru
            if (($msiProc.ExitCode -eq 0) -and (Test-Path $tcltkAdm)) {
                Copy-Item -Path (Join-Path $tcltkAdm "*") -Destination $PortablePyDir -Recurse -Force -Exclude "*.msi"
            }
            Remove-Item -Recurse -Force $tcltkAdm, $tcltkMsi -ErrorAction SilentlyContinue
        } catch {
            Write-Host "[INFO] Optional Tcl/Tk package skipped (browser app-window mode will be used)." -ForegroundColor DarkGray
        }
    } catch {
        Write-Host "[FALLBACK] Downloading official python.org installer into isolated project folder..." -ForegroundColor Yellow
        $pySetupExe = Join-Path $CacheDir "python-3.12.8-amd64.exe"
        Download-FileFast -Url "https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe" -OutFile $pySetupExe -Label "Official Python 3.12.8 Installer (64-bit)"
        $installArgs = @(
            "/quiet",
            "InstallAllUsers=0",
            "TargetDir=`"$PortablePyDir`"",
            "PrependPath=0",
            "Shortcuts=0",
            "Include_launcher=0",
            "Include_doc=0",
            "Include_test=0",
            "Include_tcltk=1",
            "Include_pip=1"
        )
        [void](Start-Process -FilePath $pySetupExe -ArgumentList $installArgs -Wait -PassThru)
        Remove-Item -Force $pySetupExe -ErrorAction SilentlyContinue
    }

    if (-not (Test-Path $portablePyExe)) {
        throw "Portable Python setup did not complete ($portablePyExe not found)."
    }
    return $portablePyExe
}

function Ensure-FolderLocalPythonAndDeps {
    Write-Host "[STEP 1/5] Checking Python interpreter and scientific dependencies..." -ForegroundColor Cyan
    Ensure-VcRedistIfMissing

    $venvPy = Join-Path $LocalVenvDir "Scripts\python.exe"
    $projVenvPy = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    if ((Test-Path $projVenvPy) -and (Test-AllRequiredPackages $projVenvPy)) {
        Write-Host "[OK] Project virtual environment (.venv) ready: $projVenvPy" -ForegroundColor Green
        return $projVenvPy
    }
    if ((Test-Path $venvPy) -and (Test-AllRequiredPackages $venvPy)) {
        Write-Host "[OK] Folder-local virtual environment (.runtime\venv) ready: $venvPy" -ForegroundColor Green
        return $venvPy
    }

    $basePyExe = $null
    $basePyArgs = @()

    $portablePyExe = Join-Path $PortablePyDir "python.exe"
    if ((Test-Path $portablePyExe) -and (Test-PythonInterpreter -ExePath $portablePyExe -AllowNoTk)) {
        $basePyExe = $portablePyExe
    }

    if (-not $basePyExe) {
        $localProg = $env:LOCALAPPDATA
        $progFiles = $env:ProgramFiles
        $candidates = @()
        if ($localProg) {
            $candidates += Get-ChildItem -Path (Join-Path $localProg "Programs\Python\Python3*\python.exe") -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -ExpandProperty FullName
        }
        if ($progFiles) {
            $candidates += Get-ChildItem -Path (Join-Path $progFiles "Python3*\python.exe") -ErrorAction SilentlyContinue | Sort-Object FullName -Descending | Select-Object -ExpandProperty FullName
        }
        $cmdPy = Get-Command python -ErrorAction SilentlyContinue
        if ($cmdPy -and $cmdPy.Source -and ($cmdPy.Source -notmatch "WindowsApps")) {
            $candidates += $cmdPy.Source
        }
        foreach ($c in $candidates) {
            if (Test-PythonInterpreter -ExePath $c) {
                $basePyExe = $c
                break
            }
        }
        if (-not $basePyExe) {
            foreach ($c in $candidates) {
                if (Test-PythonInterpreter -ExePath $c -AllowNoTk) {
                    $basePyExe = $c
                    break
                }
            }
        }
    }

    if (-not $basePyExe) {
        $cmdPyLauncher = Get-Command py -ErrorAction SilentlyContinue
        if ($cmdPyLauncher -and (Test-PythonInterpreter -ExePath $cmdPyLauncher.Source -PrefixArgs @("-3") -AllowNoTk)) {
            $basePyExe = $cmdPyLauncher.Source
            $basePyArgs = @("-3")
        }
    }

    if (-not $basePyExe) {
        Write-Host "[SETUP] No compatible Python installation found; installing portable Python 3.12.8 into .runtime\python..." -ForegroundColor Yellow
        $basePyExe = Install-PortablePythonToRuntime
        $basePyArgs = @()
        Write-Host "[OK] Portable Python ready: $basePyExe" -ForegroundColor Green
    } else {
        Write-Host "[OK] Compatible Python detected: $basePyExe $($basePyArgs -join ' ')" -ForegroundColor Green
    }

    if (Test-Path $PortablePyDir) {
        $env:PATH = "$PortablePyDir;$PortablePyDir\Scripts;$env:PATH"
    }

    if (-not (Test-Path $venvPy)) {
        Write-Host "[SETUP] Creating isolated virtual environment (.runtime\venv)..." -ForegroundColor Yellow
        $venvExit = Invoke-NativeCommand -FilePath $basePyExe -Arguments ($basePyArgs + @("-m", "venv", $LocalVenvDir))
        if (($venvExit -ne 0) -or (-not (Test-Path $venvPy))) {
            throw "Failed to create virtual environment (.runtime\venv) (Exit code: $venvExit)."
        }
    }

    $env:PATH = "$(Join-Path $LocalVenvDir 'Scripts');$env:PATH"

    if (-not (Test-AllRequiredPackages $venvPy)) {
        Write-Host "[SETUP] Installing Python dependencies into .runtime\venv..." -ForegroundColor Yellow
        [void](Invoke-NativeCommand -FilePath $venvPy -Arguments @("-m", "pip", "install", "--upgrade", "pip", "wheel", "--quiet"))
        $pipExit = Invoke-NativeCommand -FilePath $venvPy -Arguments @("-m", "pip", "install", "--prefer-binary", "-r", (Join-Path $ProjectRoot "requirements.txt"))
        if ($pipExit -ne 0) {
            throw "Error while installing requirements.txt packages (Exit code: $pipExit)."
        }
        if (-not (Test-AllRequiredPackages $venvPy)) {
            throw "Packages were installed, but module verification failed."
        }
    }
    Write-Host "[OK] All Python libraries (Flask, numpy, PyMuPDF, Pillow, certifi, PyInstaller) verified." -ForegroundColor Green
    return $venvPy
}

function Get-OllamaTagsOnline {
    try {
        $resp = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -Method Get -TimeoutSec 3 -ErrorAction Stop
        if ($null -ne $resp -and $null -ne $resp.models) {
            return @($resp.models | ForEach-Object { [string]$_.name })
        }
        return @()
    } catch {
        return $null
    }
}

function Select-RecommendedBaseModel {
    try {
        $cs = Get-CimInstance -ClassName Win32_ComputerSystem -ErrorAction Stop
        $ramGb = [math]::Round($cs.TotalPhysicalMemory / 1GB, 1)
        if ($ramGb -lt 7.5) {
            Write-Host "[INFO] System RAM is $ramGb GB (<7.5 GB); selecting lightweight local model (qwen2.5:3b)." -ForegroundColor Yellow
            return "qwen2.5:3b"
        }
    } catch {}
    return "qwen3.5:4b"
}

function Ensure-OllamaAndLocalModel {
    param([bool]$KeepRunningAfterSetup = $false)

    if ($SkipOllama) {
        Write-Host "[SKIPPED] Local Ollama model setup skipped via -SkipOllama." -ForegroundColor DarkGray
        return
    }

    Write-Host ""
    Write-Host "[STEP 2/5] Checking local offline LLM runtime (Ollama)..." -ForegroundColor Cyan

    # SAFETY RULE 1: Never restart or disturb an already running Ollama service!
    $onlineModels = Get-OllamaTagsOnline
    if ($null -ne $onlineModels) {
        $hasReadyModel = $false
        foreach ($m in $onlineModels) {
            if ($m -match "(?i)(nasa|qwen3\.5|qwen3:|qwen2\.5)") {
                $hasReadyModel = $true
                break
            }
        }
        if ($hasReadyModel) {
            Write-Host "[OK] Active local Ollama service and model detected (existing setup left untouched)." -ForegroundColor Green
            return
        }

        $sysOllamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
        $sysOllamaExe = if ($sysOllamaCmd) { $sysOllamaCmd.Source } else { Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe" }
        if ($sysOllamaExe -and (Test-Path $sysOllamaExe)) {
            $baseTag = Select-RecommendedBaseModel
            Write-Host "[SETUP] Pulling '$baseTag' into active Ollama service (existing settings untouched)..." -ForegroundColor Yellow
            [void](Invoke-NativeCommand -FilePath $sysOllamaExe -Arguments @("pull", $baseTag))
            $mfTemplate = Join-Path $ScriptDir "Modelfile.nasa-portable"
            if ((Test-Path $mfTemplate) -and ($onlineModels -notcontains "qwen3.5-nasa-portable:4b")) {
                $tmpMf = Join-Path $CacheDir "Modelfile.nasa-gen"
                $mfRaw = [System.IO.File]::ReadAllText($mfTemplate).Replace("__BASE_MODEL__", $baseTag)
                Write-Utf8NoBom -FilePath $tmpMf -Text $mfRaw
                [void](Invoke-NativeCommand -FilePath $sysOllamaExe -Arguments @("create", "qwen3.5-nasa-portable:4b", "-f", $tmpMf))
                Remove-Item -Force $tmpMf -ErrorAction SilentlyContinue
            }
            Write-Host "[OK] Local model ready." -ForegroundColor Green
            return
        }
    }

    $installedSysOllama = $null
    $cmdOl = Get-Command ollama -ErrorAction SilentlyContinue
    if ($cmdOl -and $cmdOl.Source -and (Test-Path $cmdOl.Source)) {
        $installedSysOllama = $cmdOl.Source
    } elseif ($env:LOCALAPPDATA -and (Test-Path (Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"))) {
        $installedSysOllama = Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"
    }

    $targetOllamaExe = $null
    $usingPortable = $false

    if ($installedSysOllama) {
        Write-Host "[OK] Installed system Ollama detected: $installedSysOllama" -ForegroundColor Green
        $targetOllamaExe = $installedSysOllama
    } else {
        $usingPortable = $true
        New-Item -ItemType Directory -Force -Path $PortableOllamaDir, $PortableModelsDir | Out-Null
        $foundPortExe = Get-ChildItem -Path $PortableOllamaDir -Filter "ollama.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        if (-not $foundPortExe) {
            $ollamaZip = Join-Path $CacheDir "ollama-windows-amd64.zip"
            $ollamaUrl = "https://github.com/ollama/ollama/releases/latest/download/ollama-windows-amd64.zip"
            Download-FileFast -Url $ollamaUrl -OutFile $ollamaZip -Label "Portable Ollama Engine (Windows x64 ZIP)"
            Write-Host "[SETUP] Extracting portable Ollama into .runtime\ollama..." -ForegroundColor Yellow
            Add-Type -AssemblyName System.IO.Compression.FileSystem
            [System.IO.Compression.ZipFile]::ExtractToDirectory($ollamaZip, $PortableOllamaDir)
            Remove-Item -Force $ollamaZip -ErrorAction SilentlyContinue
            $foundPortExe = Get-ChildItem -Path $PortableOllamaDir -Filter "ollama.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        }
        if (-not $foundPortExe) {
            Write-Host "[WARN] Portable ollama.exe not found; continuing with the built-in Analytical Physics Solver." -ForegroundColor Yellow
            return
        }
        $targetOllamaExe = $foundPortExe.FullName
        Write-Host "[OK] Folder-local portable Ollama ready: $targetOllamaExe" -ForegroundColor Green
    }

    $prevOllamaModels = $env:OLLAMA_MODELS
    $prevOllamaHost = $env:OLLAMA_HOST
    $startedProc = $null

    try {
        if ($usingPortable) {
            $env:OLLAMA_MODELS = $PortableModelsDir
            $env:OLLAMA_HOST = "127.0.0.1:11434"
        }

        if ($null -eq (Get-OllamaTagsOnline)) {
            Write-Host "[START] Starting local Ollama service..." -ForegroundColor Yellow
            $startedProc = Start-Process -FilePath $targetOllamaExe -ArgumentList "serve" -WorkingDirectory (Split-Path -Parent $targetOllamaExe) -WindowStyle Hidden -PassThru
            $ready = $false
            for ($i = 0; $i -lt 35; $i++) {
                Start-Sleep -Milliseconds 800
                if ($null -ne (Get-OllamaTagsOnline)) {
                    $ready = $true
                    break
                }
            }
            if (-not $ready) {
                Write-Host "[WARN] Ollama did not respond within 28 s; continuing with the built-in Analytical Physics Solver." -ForegroundColor Yellow
                return
            }
        }

        $currentTags = Get-OllamaTagsOnline
        $alreadyHasModel = $false
        if ($null -ne $currentTags) {
            foreach ($t in $currentTags) {
                if ($t -match "(?i)(nasa|qwen3\.5|qwen3:|qwen2\.5)") {
                    $alreadyHasModel = $true
                    break
                }
            }
        }

        if (-not $alreadyHasModel) {
            $baseTag = Select-RecommendedBaseModel
            Write-Host "[SETUP] Downloading local science model ($baseTag) into folder..." -ForegroundColor Yellow
            $pullExit = Invoke-NativeCommand -FilePath $targetOllamaExe -Arguments @("pull", $baseTag)
            if ($pullExit -eq 0) {
                $mfTemplate = Join-Path $ScriptDir "Modelfile.nasa-portable"
                if (Test-Path $mfTemplate) {
                    $tmpMf = Join-Path $CacheDir "Modelfile.nasa-gen"
                    $mfRaw = [System.IO.File]::ReadAllText($mfTemplate).Replace("__BASE_MODEL__", $baseTag)
                    Write-Utf8NoBom -FilePath $tmpMf -Text $mfRaw
                    [void](Invoke-NativeCommand -FilePath $targetOllamaExe -Arguments @("create", "qwen3.5-nasa-portable:4b", "-f", $tmpMf))
                    Remove-Item -Force $tmpMf -ErrorAction SilentlyContinue
                }
                Write-Host "[OK] Local science model (qwen3.5-nasa-portable:4b) is ready." -ForegroundColor Green
            } else {
                Write-Host "[WARN] Model download did not complete (Code: $pullExit); continuing with the Analytical Physics Solver." -ForegroundColor Yellow
            }
        } else {
            Write-Host "[OK] Local science model is already installed." -ForegroundColor Green
        }
    } finally {
        if (($null -ne $startedProc) -and (-not $KeepRunningAfterSetup)) {
            try {
                if (-not $startedProc.HasExited) {
                    Stop-Process -Id $startedProc.Id -Force -ErrorAction SilentlyContinue
                }
            } catch {}
        }
        if ($usingPortable -and (-not $KeepRunningAfterSetup)) {
            $env:OLLAMA_MODELS = $prevOllamaModels
            $env:OLLAMA_HOST = $prevOllamaHost
        }
    }
}

try {
    $PythonExe = Ensure-FolderLocalPythonAndDeps

    try {
        Ensure-OllamaAndLocalModel -KeepRunningAfterSetup:($Action -eq "RunApp")
    } catch {
        Write-Host "[WARN] Local Ollama setup notice: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "       Continuing in 100% offline Analytical Physics Solver mode." -ForegroundColor Yellow
    }

    if ($Action -eq "VerifyEnvOnly") {
        Write-Host ""
        Write-Host "[SUCCESS] Environment setup and verification completed." -ForegroundColor Green
        exit 0
    }

    if ($Action -eq "RunApp") {
        Write-Host ""
        Write-Host "[STEP 3/3] Launching ALTAR-NASA v6.3..." -ForegroundColor Cyan
        $appExit = Invoke-NativeCommand -FilePath $PythonExe -Arguments @((Join-Path $ProjectRoot "main_nasa.py"))
        exit $appExit
    }

    # Action == BuildExe
    Write-Host ""
    Write-Host "[STEP 3/5] Regenerating desktop icon and serverless static web bundle..." -ForegroundColor Cyan
    $icoExit = Invoke-NativeCommand -FilePath $PythonExe -Arguments @((Join-Path $ProjectRoot "nasa_icon.py"))
    if ($icoExit -ne 0) { throw "nasa_icon.py failed (Exit code: $icoExit)." }

    $webExit = Invoke-NativeCommand -FilePath $PythonExe -Arguments @((Join-Path $ProjectRoot "build_serverless_web.py"))
    if ($webExit -ne 0) { throw "build_serverless_web.py failed (Exit code: $webExit)." }

    Write-Host ""
    Write-Host "[STEP 4/5] Running automated self-tests (--self-test)..." -ForegroundColor Cyan
    $stExit = Invoke-NativeCommand -FilePath $PythonExe -Arguments @((Join-Path $ProjectRoot "main_nasa.py"), "--self-test")
    if ($stExit -ne 0) { throw "Self-test failed (Exit code: $stExit)!" }

    Write-Host ""
    Write-Host "[STEP 5/5] Compiling single-file standalone Nasa_4.exe via PyInstaller..." -ForegroundColor Cyan
    $pyiExit = Invoke-NativeCommand -FilePath $PythonExe -Arguments @("-m", "PyInstaller", "--noconfirm", "--clean", (Join-Path $ProjectRoot "Nasa_4.spec"))
    if ($pyiExit -ne 0) { throw "PyInstaller build failed (Exit code: $pyiExit)!" }

    $BuiltExe = Join-Path $ProjectRoot "dist\Nasa_4.exe"
    $RootExe = Join-Path $ProjectRoot "Nasa_4.exe"
    if (-not (Test-Path $BuiltExe)) {
        throw "dist\Nasa_4.exe was not produced!"
    }

    Copy-Item -Path $BuiltExe -Destination $RootExe -Force
    $exeExit = Invoke-NativeCommand -FilePath $RootExe -Arguments @("--self-test")
    if ($exeExit -ne 0) {
        throw "Compiled Nasa_4.exe did not pass --self-test (Exit code: $exeExit)."
    }

    Remove-Item -Recurse -Force (Join-Path $ProjectRoot "build") -ErrorAction SilentlyContinue

    $sizeMb = [math]::Round((Get-Item $RootExe).Length / 1MB, 1)
    Write-Host ""
    Write-Host "==================================================================" -ForegroundColor Green
    Write-Host "  [SUCCESS] Nasa_4.exe built and verified ($sizeMb MB)" -ForegroundColor Green
    Write-Host "  1) Project Root Copy : $RootExe" -ForegroundColor White
    Write-Host "  2) Dist Folder Copy  : $BuiltExe" -ForegroundColor Gray
    Write-Host "==================================================================" -ForegroundColor Green
    exit 0
} catch {
    Write-Host ""
    Write-Host "==================================================================" -ForegroundColor Red
    Write-Host "  [ERROR] Operation did not complete: $($_.Exception.Message)" -ForegroundColor Red
    if (-not (Test-Path (Join-Path $ProjectRoot "web_serverless\index.html"))) {
        exit 1
    }
    if ($Action -eq "RunApp") {
        Write-Host "  [FALLBACK] Opening zero-install browser edition (web_serverless\index.html)..." -ForegroundColor Yellow
        Start-Process (Join-Path $ProjectRoot "web_serverless\index.html")
    }
    Write-Host "==================================================================" -ForegroundColor Red
    exit 1
}
