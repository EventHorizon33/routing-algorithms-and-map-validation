$root = Split-Path $PSScriptRoot -Parent

$jar = Join-Path $root "tools\graphhopper-web-11.0.jar"
$config = Join-Path $root "graphhopper\config.yml"
$pbf = Join-Path $root "data\southern-zone-latest.osm.pbf"
$graphhopperDir = Split-Path $config -Parent
$graphCache = Join-Path $graphhopperDir "graph-cache"

# Download GraphHopper JAR
if (-not (Test-Path $jar)) {
    Invoke-WebRequest -Uri https://github.com/graphhopper/graphhopper/releases/download/11.0/graphhopper-web-11.0.jar -OutFile $jar
}

# Download GraphHopper's example config
if (-not (Test-Path $config)) {
    Invoke-WebRequest -Uri https://raw.githubusercontent.com/graphhopper/graphhopper/11.0/config-example.yml -OutFile $config
}

# Download Southern Zone OSM extract (covers Goa — Geofabrik has no standalone Goa file)
if (-not (Test-Path $pbf)) {
    Invoke-WebRequest -Uri https://download.geofabrik.de/asia/india/southern-zone-latest.osm.pbf -OutFile $pbf
}

# Set the PBF path directly inside config.yml instead of passing -D on the command line
# (avoids a PowerShell argument-parsing quirk with -Dkey=value style flags)
$configContent = Get-Content $config -Raw
$pbfReference = "../data/$([System.IO.Path]::GetFileName($pbf))"
$configContent = $configContent -replace 'datareader\.file:\s*".*"', "datareader.file: `"$pbfReference`""
Set-Content $config -Value $configContent -NoNewline

# Locate java executable (check PATH first, then JAVA_HOME)
$javaCmd = (Get-Command java -ErrorAction SilentlyContinue).Source
if (-not $javaCmd -and $env:JAVA_HOME) {
    $candidate = Join-Path $env:JAVA_HOME 'bin\java.exe'
    if (Test-Path $candidate) { $javaCmd = $candidate }
}
if (-not $javaCmd) {
    Write-Error "Java executable not found. Ensure Java is on PATH or set JAVA_HOME."
    exit 1
}

# Both the application and its admin endpoint must be free before rebuilding.
# Check this before touching graph-cache: a second GraphHopper instance cannot
# bind to an already-running server, and rebuilding would be wasted work.
foreach ($port in 8989, 8990) {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $port)
    try {
        $listener.Start()
    }
    catch {
        Write-Error "localhost:$port is already in use. Stop the existing GraphHopper server, or use it directly at http://localhost:8989."
        exit 1
    }
    finally {
        $listener.Stop()
    }
}

# A changed custom model changes GraphHopper's stored configuration hash, so the
# old graph cannot be reused. Remove only this project's generated cache.
if (Test-Path $graphCache) {
    Remove-Item -LiteralPath $graphCache -Recurse -Force
}

# Run from the config directory so relative paths in config.yml (including the
# custom model and graph-cache) resolve inside graphhopper/.
Push-Location $graphhopperDir
try {
    # Import map data (builds the routable graph from the PBF referenced in config.yml)
    & $javaCmd -jar $jar import $config
    if ($LASTEXITCODE -ne 0) {
        throw "GraphHopper import failed with exit code $LASTEXITCODE."
    }

    # Start GraphHopper server
    & $javaCmd -jar $jar server $config
}
finally {
    Pop-Location
}
