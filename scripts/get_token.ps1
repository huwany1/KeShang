# 脚本: scripts/get_token.ps1
# 作用: 调用网关 /auth/login 获取 accessToken，设置到当前会话环境变量 TOKEN，并输出到控制台与 .build/token.txt。
# 用法示例：
#   pwsh -File scripts/get_token.ps1 -Email "t@example.com" -Password "pass1234" -BaseUrl "http://localhost:8080"

param(
    [string]$Email = "t@example.com",
    [string]$Password = "pass1234",
    [string]$BaseUrl = "http://localhost:8080"
)

function Invoke-LoginRequest {
    param(
        [Parameter(Mandatory = $true)][string]$BaseUrl,
        [Parameter(Mandatory = $true)][string]$Email,
        [Parameter(Mandatory = $true)][string]$Password
    )

    $loginUrl = "$BaseUrl/auth/login"
    $body = @{ email = $Email; password = $Password } | ConvertTo-Json -Depth 3

    try {
        $response = Invoke-RestMethod -Method POST -Uri $loginUrl -ContentType 'application/json' -Body $body -TimeoutSec 15
        if (-not $response.accessToken) { throw "No accessToken in response" }
        return [string]$response.accessToken
    } catch {
        throw "Login request failed: $($_.Exception.Message)"
    }
}

function Save-Token {
    param([Parameter(Mandatory = $true)][string]$Token)
    $env:TOKEN = $Token
    $outDir = Join-Path -Path "." -ChildPath ".build"
    if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }
    $outFile = Join-Path -Path $outDir -ChildPath "token.txt"
    Set-Content -Path $outFile -Value $Token -Encoding UTF8
    return $outFile
}

try {
    Write-Host "Logging in to $BaseUrl ..." -ForegroundColor Cyan
    $token = Invoke-LoginRequest -BaseUrl $BaseUrl -Email $Email -Password $Password
    $filePath = Save-Token -Token $token
    Write-Host "Token saved to env: TOKEN and file: $filePath" -ForegroundColor Green
    Write-Host "TOKEN=$token" -ForegroundColor Yellow
} catch {
    Write-Error $_
    exit 1
}


