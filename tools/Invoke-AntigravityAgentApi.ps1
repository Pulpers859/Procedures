<#
.SYNOPSIS
Discovers the running Google Antigravity language server and drives its agentapi CLI.

.DESCRIPTION
Antigravity's desktop app starts a localhost-only language_server.exe that rotates
its listening port and CSRF token on every restart. This helper performs the
discovery step (process scan, CSRF parse, highest listening port), exports the
env vars the agentapi CLI expects, and dispatches the three CLI verbs used for
image generation. See docs/visual-assets/ANTIGRAVITY_WORKFLOW.md.

.EXAMPLE
.\tools\Invoke-AntigravityAgentApi.ps1 -Command PrintEnv

.EXAMPLE
.\tools\Invoke-AntigravityAgentApi.ps1 -Command NewConversation `
  -Title "Cric Membrane Draft 1" `
  -PromptFile "tmp\visual-drafts\antigravity\cric_membrane\01_image_prompt.txt" `
  -PassPromptFileAsAtPath

.EXAMPLE
.\tools\Invoke-AntigravityAgentApi.ps1 -Command SendMessage `
  -ConversationId "<id>" -PromptFile "...\02_repair.txt" -PassPromptFileAsAtPath
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('PrintEnv', 'NewConversation', 'SendMessage', 'GetConversationMetadata')]
    [string]$Command,

    [string]$Title,
    [string]$Prompt,
    [string]$PromptFile,
    [switch]$PassPromptFileAsAtPath,
    [string]$ConversationId,
    [string]$Model = 'pro',
    # Machine-specific. Persist it once via $env:ANTIGRAVITY_PROJECT_ID.
    [string]$ProjectId = $env:ANTIGRAVITY_PROJECT_ID,
    # Machine-specific install path of the agentapi CLI.
    [string]$AgentApiPath = (Join-Path $env:USERPROFILE '.gemini\antigravity\bin\agentapi.bat')
)

$ErrorActionPreference = 'Stop'

function Get-AntigravityServer {
    $candidates = @(Get-CimInstance Win32_Process -Filter "Name = 'language_server.exe'" |
        Where-Object { $_.CommandLine -match '--csrf_token' })
    if ($candidates.Count -eq 0) {
        throw 'No running language_server.exe with a CSRF token was found. Launch the Antigravity desktop app first; it cannot be booted headlessly.'
    }
    $server = $candidates[0]

    if ($server.CommandLine -notmatch '--csrf_token[=\s]+"?([A-Za-z0-9_\-]+)') {
        throw "Could not parse --csrf_token from the language_server command line (PID $($server.ProcessId))."
    }
    $csrfToken = $Matches[1]

    $ports = @(Get-NetTCPConnection -OwningProcess $server.ProcessId -State Listen -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty LocalPort -Unique | Sort-Object)
    if ($ports.Count -eq 0) {
        throw "language_server.exe (PID $($server.ProcessId)) has no listening ports yet. Wait a few seconds after app launch and retry."
    }

    [pscustomobject]@{
        ProcessId = $server.ProcessId
        # The higher listening port is the HTTPS port the CLI talks to.
        Address   = "127.0.0.1:$($ports[-1])"
        CsrfToken = $csrfToken
        Ports     = $ports
    }
}

function Resolve-PromptArgument {
    if ($PromptFile) {
        $resolved = (Resolve-Path -LiteralPath $PromptFile).Path
        if ($PassPromptFileAsAtPath) {
            return "@$resolved"
        }
        $content = Get-Content -LiteralPath $resolved -Raw
        if ($content -match "\r?\n.") {
            Write-Warning 'Multi-line prompt passed as a plain string: Antigravity only receives the first line. Re-run with -PassPromptFileAsAtPath.'
        }
        return $content.TrimEnd()
    }
    if ($Prompt) {
        if ($Prompt -match "\r?\n.") {
            Write-Warning 'Multi-line -Prompt strings lose everything after the first line. Write the prompt to a file and use -PromptFile with -PassPromptFileAsAtPath.'
        }
        return $Prompt
    }
    throw "Command '$Command' requires -Prompt or -PromptFile."
}

$server = Get-AntigravityServer
$env:ANTIGRAVITY_LS_ADDRESS = $server.Address
$env:ANTIGRAVITY_CSRF_TOKEN = $server.CsrfToken
if ($ProjectId) {
    $env:ANTIGRAVITY_PROJECT_ID = $ProjectId
}
elseif (-not $env:ANTIGRAVITY_PROJECT_ID) {
    Write-Warning 'ANTIGRAVITY_PROJECT_ID is not set. It is machine-specific; pass -ProjectId or set the env var if the CLI rejects requests.'
}

if ($Command -eq 'PrintEnv') {
    [pscustomobject]@{
        ProcessId              = $server.ProcessId
        ANTIGRAVITY_LS_ADDRESS = $env:ANTIGRAVITY_LS_ADDRESS
        ANTIGRAVITY_CSRF_TOKEN = $env:ANTIGRAVITY_CSRF_TOKEN
        ANTIGRAVITY_PROJECT_ID = $env:ANTIGRAVITY_PROJECT_ID
        ListeningPorts         = $server.Ports -join ', '
        AgentApiPath           = $AgentApiPath
        AgentApiExists         = (Test-Path -LiteralPath $AgentApiPath)
    } | Format-List
    return
}

if (-not (Test-Path -LiteralPath $AgentApiPath)) {
    throw "agentapi CLI not found at '$AgentApiPath'. The install path is machine-specific; pass -AgentApiPath."
}

switch ($Command) {
    'NewConversation' {
        if (-not $Title) { throw 'NewConversation requires -Title.' }
        $promptArg = Resolve-PromptArgument
        & $AgentApiPath new-conversation "--model=$Model" "--title=$Title" $promptArg
    }
    'SendMessage' {
        if (-not $ConversationId) { throw 'SendMessage requires -ConversationId.' }
        $promptArg = Resolve-PromptArgument
        & $AgentApiPath send-message $ConversationId $promptArg
    }
    'GetConversationMetadata' {
        if (-not $ConversationId) { throw 'GetConversationMetadata requires -ConversationId.' }
        & $AgentApiPath get-conversation-metadata $ConversationId
    }
}
exit $LASTEXITCODE
