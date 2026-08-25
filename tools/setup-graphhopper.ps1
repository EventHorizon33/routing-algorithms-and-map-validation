# Download GraphHopper JAR
if (-not (Test-Path "graphhopper-web-11.0.jar")) {
    Invoke-WebRequest -Uri https://github.com/graphhopper/graphhopper/releases/download/11.0/graphhopper-web-11.0.jar -OutFile graphhopper-web-11.0.jar
}

# Download GraphHopper's example config
if (-not (Test-Path "config.yml")) {
    Invoke-WebRequest -Uri https://raw.githubusercontent.com/graphhopper/graphhopper/11.0/config-example.yml -OutFile config.yml
}

# Download Southern Zone OSM extract (covers Goa — Geofabrik has no standalone Goa file)
if (-not (Test-Path "southern-zone-latest.osm.pbf")) {
    Invoke-WebRequest -Uri https://download.geofabrik.de/asia/india/southern-zone-latest.osm.pbf -OutFile southern-zone-latest.osm.pbf
}

# Set the PBF path directly inside config.yml instead of passing -D on the command line
# (avoids a PowerShell argument-parsing quirk with -Dkey=value style flags)
$configContent = Get-Content config.yml -Raw
$configContent = $configContent -replace 'datareader\.file:\s*".*"', 'datareader.file: "southern-zone-latest.osm.pbf"'
Set-Content config.yml -Value $configContent -NoNewline

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

# Import map data (builds the routable graph from the PBF referenced in config.yml)
& $javaCmd -jar graphhopper-web-11.0.jar import config.yml

# Start GraphHopper server
& $javaCmd -jar graphhopper-web-11.0.jar server config.yml