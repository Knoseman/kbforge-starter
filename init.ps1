# KBForge Windows Init Script
# Run by right-clicking and selecting "Run with PowerShell"

$vault = Split-Path -Parent $MyInvocation.MyCommand.Definition

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

function Slugify {
    param([string]$s)
    $s = $s.ToLower().Replace(" ", "-") -replace "[^a-z0-9-]", "-" -replace "-+", "-"
    return $s.Trim("-")
}

function Prompt-User {
    param([string]$question, [string]$example)
    while ($true) {
        $hint = if ($example) { " (e.g. $example)" } else { "" }
        $val = Read-Host "$question$hint"
        if ($val.Trim()) { return $val.Trim() }
        Write-Host "  ✗ This field is required." -ForegroundColor Red
    }
}

function Prompt-List {
    param([string]$question, [string]$example, [int]$minCount=1, [int]$maxCount=5)
    $hint = if ($example) { " (e.g. $example)" } else { "" }
    Write-Host "$question$hint"
    Write-Host "  Enter $minCount–$maxCount items, one per line. Empty line to finish."
    $items = New-Object System.Collections.Generic.List[string]
    while ($items.Count -lt $maxCount) {
        $val = Read-Host "  $($items.Count + 1)"
        if (-not $val.Trim()) {
            if ($items.Count -ge $minCount) { break }
            Write-Host "  ✗ Please enter at least $minCount item(s)." -ForegroundColor Red
            continue
        }
        $items.Add((Slugify $val.Trim()))
    }
    return $items
}

# ---------------------------------------------------------------------------
# Steps
# ---------------------------------------------------------------------------

Write-Host "`n" + "=" * 60 -ForegroundColor Cyan
Write-Host "  KBForge — init" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

$domain = Slugify (Prompt-User -question "1. Domain slug (your primary knowledge area)" -example "my-domain")
$team = Prompt-User -question "2. Team / company name" -example "My Team"
$topics = Prompt-List -question "3. Seed topics (key concepts you'll document)" -example "authentication, webhooks, onboarding" -minCount 3 -maxCount 5

Write-Host "`n  Domain slug : $domain"
Write-Host "  Team name   : $team"
Write-Host "  Topics      : $($topics -join ', ')"
Write-Host ""
$confirm = Read-Host "Looks good? (y/n)"
if ($confirm -ne 'y' -and $confirm -ne 'yes') {
    Write-Host "Aborted." -ForegroundColor Yellow
    exit
}

Write-Host "`nApplying changes...`n" -ForegroundColor Cyan

# 1. Patch topics.yaml
$topicsPath = Join-Path $vault "01 Reference/topics.yaml"
$topicsContent = Get-Content $topicsPath -Encoding utf8
$demoDomains = "  - example-domain    # example: replace with your API or product domain"
$newDomains = "  - $domain`n  - ops`n  - ai-practices"
$topicsContent = $topicsContent.Replace($demoDomains, $newDomains)
$seedBlock = ($topics | ForEach-Object { "  - $_" }) -join "`n"
$topicsContent = $topicsContent.Replace("  # Your seed topics", "  # Your seed topics`n$seedBlock")
$topicsContent | Set-Content $topicsPath -Encoding utf8
Write-Host "  ✓ topics.yaml — domain set to '$domain', $($topics.Count) seed topics added" -ForegroundColor Green

# 2. Patch AGENTS.md files
Get-ChildItem -Path $vault -Recurse -Filter "AGENTS.md" | ForEach-Object {
    $content = Get-Content $_.FullName -Encoding utf8 -Raw
    $content = $content.Replace("YOUR_DOMAIN", $domain)
    $content = $content.Replace("YOUR_TEAM_NAME", $team)
    $content | Set-Content $_.FullName -Encoding utf8
}
Write-Host "  ✓ AGENTS.md files updated" -ForegroundColor Green

# 3. Clean up logs
foreach ($log in @("05 Iteration Logs/KB Gaps.md", "05 Iteration Logs/Ingestion Log.md")) {
    $path = Join-Path $vault $log
    if (Test-Path $path) {
        $text = Get-Content $path -Encoding utf8 -Raw
        $header = $text.Split("---")[0] + "---"
        $header + "`n`n### [Template] Add your first entry here..." | Set-Content $path -Encoding utf8
        Write-Host "  ✓ Cleared example entries from $log" -ForegroundColor Green
    }
}

# 4. Scaffold starting files
$today = Get-Date -Format "yyyy-MM-dd"
$accountPath = Join-Path $vault "03 Accounts/(C) $team.md"
@"
---
account: $team
integration_type: api
product: $domain
phase: discovery
status: active
updated: $today
contacts:
  technical: ""
  commercial: ""
kb_articles: []
blockers: []
---

# $team

Add context about this account here.
"@ | Set-Content $accountPath -Encoding utf8
Write-Host "  ✓ Scaffolded account profile: 03 Accounts/(C) $team.md" -ForegroundColor Green

$firstId = "$domain.overview"
$articlePath = Join-Path $vault "01 Reference/articles/(C) $firstId.md"
$topicsYaml = "[" + (($topics | Select-Object -First 3) -join ", ") + "]"
@"
---
id: $firstId
title: $($domain.Replace("-", " ").ToUpper()) — Overview
kind: reference
domain: $domain
topics: $topicsYaml
status: provisional
updated: $today
review_due: $today
owner: ai
provenance: []
related: []
summary: "Replace this summary with a one-line answer to the most common question about $domain."
answers:
  - "What is $domain?"
  - "Give me an overview of $domain"
---

## Answer
Replace this with a 1–3 sentence answer to the most common question about $domain.

## Facts
- Add key facts, parameters, and reference data here.

## See also
"@ | Set-Content $articlePath -Encoding utf8
Write-Host "  ✓ Scaffolded first article: $firstId.md" -ForegroundColor Green

# 5. Rebuild indexes
Write-Host "`nRebuilding indexes..." -ForegroundColor Cyan
foreach ($script in @("01 Reference/scripts/build_catalog.py", "04 Skills/scripts/build_skills_index.py")) {
    $path = Join-Path $vault $script
    if (Test-Path $path) {
        python $path | ForEach-Object { Write-Host "  ✓ $_" -ForegroundColor Green }
    } else {
        Write-Host "  ⚠ $script not found — skipping"
    }
}

Write-Host "`n✓ Initialization complete." -ForegroundColor Green
