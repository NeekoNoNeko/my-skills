<#
.SYNOPSIS
    MinerU 输出整理脚本：将 MinerU 生成的嵌套目录（full.md + images/）按章节复制到新的输出目录。
.DESCRIPTION
    根据章节映射表，将每个 MinerU 子目录中的 full.md 以章节名重命名，
    连同 images/ 文件夹一起复制到输出目录中。源文件不会被修改。
.PARAMETER SourceDir
    源目录路径，包含 MinerU 输出的多个子目录。
.PARAMETER OutputDir
    输出目录路径（将在源目录内部创建）。
.PARAMETER ChapterMapping
    章节映射的 PowerShell hashtable，格式：
    @{"源目录名"="Chapter-X-Name"; ...}
.EXAMPLE
    # 定义映射后调用
    $base = "C:\path\to\source"
    $out = "$base\Introduction-to-Probability"
    $chapters = @{
        "PDF-HASH-1" = "Chapter-1-Probability-and-counting"
        "PDF-HASH-2" = "Chapter-2-Conditional-probability"
    }
    .\organize-mineru.ps1 -SourceDir $base -OutputDir $out -ChapterMapping $chapters
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$SourceDir,

    [Parameter(Mandatory=$true)]
    [string]$OutputDir,

    [Parameter(Mandatory=$true)]
    [hashtable]$ChapterMapping
)

# 创建输出目录
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

$count = 0
foreach ($src in $ChapterMapping.Keys) {
    $srcPath = Join-Path $SourceDir $src
    $chapterName = $ChapterMapping[$src]
    $outPath = Join-Path $OutputDir $chapterName

    if (-not (Test-Path $srcPath)) {
        Write-Warning "未找到源目录: $src"
        continue
    }

    # 创建章节子目录
    New-Item -ItemType Directory -Path $outPath -Force | Out-Null

    # 复制 full.md 并重命名
    $mdSrc = Join-Path $srcPath "full.md"
    if (Test-Path $mdSrc) {
        Copy-Item -Path $mdSrc -Destination (Join-Path $outPath "$chapterName.md")
    } else {
        Write-Warning "$src 中未找到 full.md"
    }

    # 复制 images/ 文件夹（保持相对路径一致）
    $imgSrc = Join-Path $srcPath "images"
    if (Test-Path $imgSrc) {
        Copy-Item -Path $imgSrc -Destination $outPath -Recurse -Force
        $imgCount = (Get-ChildItem (Join-Path $outPath "images") -Filter "*.jpg" | Measure-Object).Count
    } else {
        $imgCount = 0
    }

    Write-Host "✅ $chapterName ($imgCount 张图片)"
    $count++
}

Write-Host "`n完成！共处理 $count 个章节，输出到: $OutputDir"
