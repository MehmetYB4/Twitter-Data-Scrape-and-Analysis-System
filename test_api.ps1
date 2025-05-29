$response = Invoke-WebRequest -Uri "http://localhost:5000/analiz/liste" -Method GET
$json = $response.Content | ConvertFrom-Json
Write-Host "API Success: $($json.success)"
Write-Host "Total Count: $($json.total)"
Write-Host "Data Length: $($json.data.Length)"
if ($json.data.Length -gt 0) {
    Write-Host "First Analysis: $($json.data[0].name)"
} 