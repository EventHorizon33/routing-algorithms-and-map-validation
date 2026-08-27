$root = Split-Path $PSScriptRoot -Parent

# Task 3A is intentionally isolated from the Task 1/2 GraphHopper environment.
$jar = Join-Path $root "tools\graphhopper-web-11.0.jar"
$config = Join-Path $root "config-task3a.yml"
$pbf = Join-Path $root "data\task3a-area.osm.pbf"
$graphCache = Join-Path $root "graph-cache-task3a"

foreach ($requiredPath in @($jar, $config, $pbf)) {
    if (-not (Test-Path -LiteralPath $requiredPath)) {
        throw "Required Task 3A setup file was not found: $requiredPath"
    }
}

# Locate java executable (check PATH first, then JAVA_HOME).
$javaCmd = (Get-Command java -ErrorAction SilentlyContinue).Source
if (-not $javaCmd -and $env:JAVA_HOME) {
    $candidate = Join-Path $env:JAVA_HOME "bin\java.exe"
    if (Test-Path -LiteralPath $candidate) { $javaCmd = $candidate }
}
if (-not $javaCmd) {
    throw "Java executable not found. Ensure Java is on PATH or set JAVA_HOME."
}

# Task 3A uses dedicated ports so it can run without conflicting with the
# Task 1/2 GraphHopper service on 8989/8990.
foreach ($port in 8991, 8992) {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $port)
    try {
        $listener.Start()
    }
    catch {
        throw "localhost:$port is already in use. Stop the service using this Task 3A port before rebuilding."
    }
    finally {
        $listener.Stop()
    }
}

# Rebuild only the isolated Task 3A cache. This never targets graphhopper\graph-cache.
if (Test-Path -LiteralPath $graphCache) {
    Remove-Item -LiteralPath $graphCache -Recurse -Force
}

# config-task3a.yml uses absolute Task 3A input and cache paths, so this works
# regardless of the directory from which the script is invoked.
& $javaCmd -jar $jar import $config
if ($LASTEXITCODE -ne 0) {
    throw "Task 3A GraphHopper import failed with exit code $LASTEXITCODE."
}

& $javaCmd -jar $jar server $config
