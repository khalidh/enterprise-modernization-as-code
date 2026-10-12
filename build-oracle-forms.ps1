param(
    [string]$OracleHome = $env:ORACLE_HOME
)

$ErrorActionPreference = 'Stop'
$repoRoot = $PSScriptRoot
$python = Join-Path $repoRoot '.venv\Scripts\python.exe'
$generator = Join-Path $repoRoot 'adapters\oracle-forms\generator\generate.py'
$model = Join-Path $repoRoot 'model\customer.yaml'
$template = Join-Path $repoRoot 'adapters\oracle-forms\templates\hello_world.xml'
$xmlOutput = Join-Path $repoRoot 'generated\oracle-forms\HELLO_WORLD.xml'
$fmbOutputDirectory = Join-Path $repoRoot 'generated\oracle-forms\import-ready'
$fmbOutput = Join-Path $fmbOutputDirectory 'HELLO_WORLD.fmb'

if ([string]::IsNullOrWhiteSpace($OracleHome)) {
    throw 'ORACLE_HOME is not set. Pass -OracleHome or set the ORACLE_HOME environment variable.'
}

$converter = Join-Path $OracleHome 'forms\templates\scripts\frmxml2f.bat'
$exporter = Join-Path $OracleHome 'forms\templates\scripts\frmf2xml.bat'
foreach ($requiredPath in @($python, $generator, $model, $template, $converter, $exporter)) {
    if (-not (Test-Path -LiteralPath $requiredPath)) {
        throw "Required file not found: $requiredPath"
    }
}

$env:ORACLE_HOME = $OracleHome

Write-Host 'Running Oracle Forms tests...'
& $python -m pytest (Join-Path $repoRoot 'tests\test_oracle_forms.py') -q
if ($LASTEXITCODE -ne 0) {
    throw "Oracle Forms tests failed with exit code $LASTEXITCODE"
}

Write-Host 'Generating Oracle Forms XML...'
& $python $generator $model $template $xmlOutput
if ($LASTEXITCODE -ne 0) {
    throw "XML generation failed with exit code $LASTEXITCODE"
}

$stageDirectory = Join-Path ([System.IO.Path]::GetTempPath()) ("forms-build-" + [guid]::NewGuid().ToString('N'))
$stagedFmbDirectory = Join-Path $stageDirectory 'fmb'
$checkDirectory = Join-Path $stageDirectory 'roundtrip'
$originalJavaToolOptions = $env:JAVA_TOOL_OPTIONS
try {
    New-Item -ItemType Directory -Path $stagedFmbDirectory -Force | Out-Null
    New-Item -ItemType Directory -Path $checkDirectory -Force | Out-Null
    $javaOptions = $originalJavaToolOptions
    foreach ($requiredOption in @('-XX:+UseSerialGC', '-Xms32m', '-Xmx256m')) {
        if ($javaOptions -notmatch [regex]::Escape($requiredOption)) {
            $javaOptions = "$javaOptions $requiredOption".Trim()
        }
    }
    $env:JAVA_TOOL_OPTIONS = $javaOptions

    Write-Host 'Converting XML to FMB...'
    & $converter 'OVERWRITE=YES' "OUTPUTDIR=$stagedFmbDirectory" $xmlOutput
    if ($LASTEXITCODE -ne 0) {
        throw "Oracle XML-to-Forms conversion failed with exit code $LASTEXITCODE"
    }
    $stagedFmb = Join-Path $stagedFmbDirectory 'HELLO_WORLD.fmb'
    if (-not (Test-Path -LiteralPath $stagedFmb)) {
        throw 'Oracle XML-to-Forms conversion did not produce HELLO_WORLD.fmb'
    }

    Write-Host 'Checking the generated FMB by exporting it back to XML...'
    & $exporter "OUTPUTDIR=$checkDirectory" $stagedFmb
    if ($LASTEXITCODE -ne 0) {
        throw "Oracle Forms round-trip export failed with exit code $LASTEXITCODE"
    }

    $roundTripXml = Join-Path $checkDirectory 'HELLO_WORLD_fmb.xml'
    if (-not (Test-Path -LiteralPath $roundTripXml)) {
        throw 'Oracle Forms round-trip export did not produce the expected XML file'
    }

    [xml]$generatedDocument = Get-Content -LiteralPath $xmlOutput -Raw
    [xml]$roundTripDocument = Get-Content -LiteralPath $roundTripXml -Raw
    $generatedModule = $generatedDocument.SelectSingleNode("//*[local-name()='FormModule']")
    $roundTripModule = $roundTripDocument.SelectSingleNode("//*[local-name()='FormModule']")

    if ($null -eq $generatedModule -or $null -eq $roundTripModule) {
        throw 'FormModule is missing from the generated XML or the FMB round-trip export'
    }
    if ($generatedModule.GetAttribute('Name') -ne $roundTripModule.GetAttribute('Name')) {
        throw "Form name changed during Oracle conversion: expected '$($generatedModule.GetAttribute('Name'))', got '$($roundTripModule.GetAttribute('Name'))'"
    }

    $generatedItems = @($generatedDocument.SelectNodes("//*[local-name()='Item'][@Name]") | ForEach-Object { $_.GetAttribute('Name') })
    $roundTripItems = @($roundTripDocument.SelectNodes("//*[local-name()='Item'][@Name]") | ForEach-Object { $_.GetAttribute('Name') })
    $missingItems = @($generatedItems | Where-Object { $_ -notin $roundTripItems })
    if ($missingItems.Count -gt 0) {
        throw "Items missing after Oracle conversion: $($missingItems -join ', ')"
    }

    New-Item -ItemType Directory -Path $fmbOutputDirectory -Force | Out-Null
    Copy-Item -LiteralPath $stagedFmb -Destination $fmbOutput -Force
}
finally {
    if ([string]::IsNullOrWhiteSpace($originalJavaToolOptions)) {
        Remove-Item Env:JAVA_TOOL_OPTIONS -ErrorAction SilentlyContinue
    } else {
        $env:JAVA_TOOL_OPTIONS = $originalJavaToolOptions
    }
    Remove-Item -LiteralPath $stageDirectory -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "Build successful: $xmlOutput"
Write-Host "Build successful: $fmbOutput"