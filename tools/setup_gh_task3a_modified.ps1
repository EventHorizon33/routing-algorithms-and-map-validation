$root = Split-Path $PSScriptRoot -Parent

# This setup imports only the modified Task 3A PBF into its dedicated cache.
$jar = Join-Path $root "tools\graphhopper-web-11.0.jar"
$config = Join-Path $root "config-task3a-modified.yml"
$pbf = Join-Path $root "data\task3a-area-modified.osm.pbf"
$graphCache = Join-Path $root "graph-cache-task3a-modified"
$profile = Join-Path $root "task3a-modified-car.json"

foreach ($requiredPath in @($jar, $config, $pbf, $profile)) {
    if (-not (Test-Path -LiteralPath $requiredPath)) {
        throw "Required modified Task 3A file was not found: $requiredPath"
    }
}

$javaCmd = (Get-Command java -ErrorAction SilentlyContinue).Source
if (-not $javaCmd -and $env:JAVA_HOME) {
    $candidate = Join-Path $env:JAVA_HOME "bin\java.exe"
    if (Test-Path -LiteralPath $candidate) { $javaCmd = $candidate }
}
if (-not $javaCmd) {
    throw "Java executable not found. Ensure Java is on PATH or set JAVA_HOME."
}

foreach ($port in 8993, 8994) {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $port)
    try {
        $listener.Start()
    }
    catch {
        throw "localhost:$port is already in use. Stop the modified Task 3A service before rebuilding."
    }
    finally {
        $listener.Stop()
    }
}

# This is the only directory this script can remove before importing.
if (Test-Path -LiteralPath $graphCache) {
    Remove-Item -LiteralPath $graphCache -Recurse -Force
}

Write-Output "Modified PBF: $pbf"
Write-Output "Modified graph cache: $graphCache"
& $javaCmd -jar $jar import $config
if ($LASTEXITCODE -ne 0) {
    throw "Modified Task 3A GraphHopper import failed with exit code $LASTEXITCODE."
}

& $javaCmd -jar $jar server $config
