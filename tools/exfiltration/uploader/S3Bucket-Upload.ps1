
param(
    [string]$BucketName,
    [string]$FilePath,
    [string]$ObjectKey
)

function Show-Help {
    $Menu = @"
    
    DESCRIPTION:
        This script uploads a file to an AWS S3 Bucket via REST API.
    
    USAGE:
        ./S3BucketUpload.ps1 [-BucketName] <S3_BUCKET_NAME> [-FilePath] <LOCAL_FILE_PATH> [-ObjectKey] <OBJECT_KEY>

    OPTIONS:
        -BucketName   Name of the AWS S3 Bucket where the file is going to be uploaded.
        -ObjectKey    File unique identifier (in the bucket). Example: 'file.txt' or 'folder/file.txt'.
        -FilePath     Local path on disk where the file to upload is located.

"@
    Write-Host $Menu
}

function S3-Upload {
    param(
        [string]$BucketName,
        [string]$FilePath,
        [string]$ObjectKey
    )

    try {
        $BucketURL = "https://$BucketName.s3.amazonaws.com/$ObjectKey"

        $FileContent = Get-Content -Path $FilePath -Raw

        Invoke-RestMethod -Uri "$BucketUrl" -Method Put -Body $FileContent -ContentType "application/octet-stream" -ErrorAction Stop

        Write-Host "File uploaded successfully."

    }
    catch {
        Write-Host "[ERROR] - " $_.Exception.Message
        Exit
    }
}


# Entrypoint

if ($args -contains "-h" -or $args -contains "--help") {
    Show-Help
}
else {

    if (-not $BucketName -or -not $FilePath -or -not $ObjectKey) {
        Write-Host "[ERROR] - Missing required parameters."
        Show-Help
        Exit
    }

    S3-Upload -BucketName $BucketName -ObjectKey $ObjectKey -FilePath $FilePath
}
