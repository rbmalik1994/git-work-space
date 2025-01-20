param (
    [string]$monorepoName,
    [string]$projectName,
    [string]$libName,
    [string]$target,
    [string]$action
)

# Use current directory if monorepoName is not provided
if (-not $monorepoName) {
    $monorepoName = Get-Location
}

function Show-Help {
    Write-Host "Usage:"
    Write-Host "  --create-monorepo <monorepo_name>"
    Write-Host "  --create-project <monorepo_name> <project_name>"
    Write-Host "  --create-lib <monorepo_name> <lib_name>"
    Write-Host "  --create-docs <monorepo_name> <target>"
    exit 1
}

function Create-Monorepo {
    param (
        [string]$monorepoName
    )
    # Check if the monorepo name is provided
    if (-not $monorepoName) {
        Write-Host "Usage: --create-monorepo <monorepo_name>"
        exit 1
    }
    # Create the directory structure for the monorepo
    New-Item -ItemType Directory -Path "$monorepoName/.devcontainer","$monorepoName/projects","$monorepoName/libs","$monorepoName/docs","$monorepoName/scripts/common-scripts","$monorepoName/scripts/shell-scripts" -Force
    # Create the necessary files in the monorepo
    New-Item -ItemType File -Path "$monorepoName/.flake8","$monorepoName/README.md","$monorepoName/poetry.lock","$monorepoName/pyproject.toml","$monorepoName/dev-requirements.txt","$monorepoName/pip-requirements.txt" -Force
    Write-Host "Monorepo structure $monorepoName created."
}

function Create-Project {
    param (
        [string]$monorepoName,
        [string]$projectName
    )
    # Check if the monorepo name and project name are provided
    if (-not $monorepoName -or -not $projectName) {
        Write-Host "Usage: --create-project <monorepo_name> <project_name>"
        exit 1
    }
    # Create the directory structure for the project
    New-Item -ItemType Directory -Path "$monorepoName/projects/$projectName/.devcontainer","$monorepoName/projects/$projectName/docs","$monorepoName/projects/$projectName/src","$monorepoName/projects/$projectName/tests" -Force
    # Create the necessary files in the project
    New-Item -ItemType File -Path "$monorepoName/projects/$projectName/poetry.lock","$monorepoName/projects/$projectName/pyproject.toml","$monorepoName/projects/$projectName/run.py","$monorepoName/projects/$projectName/requirements.txt","$monorepoName/projects/$projectName/README.md" -Force
    New-Item -ItemType File -Path "$monorepoName/projects/$projectName/src/__init__.py","$monorepoName/projects/$projectName/src/pipeline.py" -Force
    New-Item -ItemType File -Path "$monorepoName/projects/$projectName/tests/__init__.py","$monorepoName/projects/$projectName/tests/test_pipeline.py" -Force
    New-Item -ItemType File -Path "$monorepoName/projects/$projectName/docs/index.md" -Force
    # Add content to the Dockerfile and devcontainer.json
    # Set-Content -Path "$monorepoName/projects/$projectName/.devcontainer/Dockerfile" -Value "# Dockerfile content here"
    Set-Content -Path "$monorepoName/projects/$projectName/.devcontainer/devcontainer.json" -Value "{`n  // devcontainer.json content here`n}"
    Write-Host "Project $projectName structure created in $monorepoName."
}

function Create-Lib {
    param (
        [string]$monorepoName,
        [string]$libName
    )
    # Check if the monorepo name and library name are provided
    if (-not $monorepoName -or -not $libName) {
        Write-Host "Usage: --create-lib <monorepo_name> <lib_name>"
        exit 1
    }
    # Create the directory structure for the library
    New-Item -ItemType Directory -Path "$monorepoName/libs/$libName/docs","$monorepoName/libs/$libName/src" -Force
    # Create the necessary files in the library
    New-Item -ItemType File -Path "$monorepoName/libs/$libName/requirements.txt","$monorepoName/libs/$libName/README.md","$monorepoName/libs/$libName/poetry.lock","$monorepoName/libs/$libName/pyproject.toml" -Force
    New-Item -ItemType File -Path "$monorepoName/libs/$libName/src/__init__.py","$monorepoName/libs/$libName/src/base_pipeline.py" -Force
    New-Item -ItemType File -Path "$monorepoName/libs/$libName/docs/index.md" -Force
    Write-Host "Library $libName structure created in $monorepoName."
}

function Create-Docs {
    param (
        [string]$monorepoName,
        [string]$target
    )
    # Check if the monorepo name and target are provided
    if (-not $monorepoName -or -not $target) {
        Write-Host "Usage: --create-docs <monorepo_name> <target>"
        exit 1
    }
    # Create the index.md file in the docs directory
    New-Item -ItemType File -Path "$monorepoName/$target/docs/index.md" -Force
    Write-Host "Docs structure created for $target in $monorepoName."
}

# Parse the action and call the appropriate function
switch ($action) {
    "create-monorepo" { Create-Monorepo -monorepoName $monorepoName }
    "create-project" { Create-Project -monorepoName $monorepoName -projectName $projectName }
    "create-lib" { Create-Lib -monorepoName $monorepoName -libName $libName }
    "create-docs" { Create-Docs -monorepoName $monorepoName -target $target }
    default { Show-Help }
}
