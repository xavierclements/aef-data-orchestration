locals {
  workflow_definitions_dir = "../workflow-definitions"

  workflow_files = {
    for filename in fileset(local.workflow_definitions_dir, "*") :
    filename => jsondecode(file("${local.workflow_definitions_dir}/${filename}"))
  }

  cloud_workflows_filenames = toset([
    for filename, file_content in local.workflow_files : filename
    if (try(file_content.engine, null) == "cloud_workflows")
  ])

  composer_filenames = [
    for filename, file_content in local.workflow_files : filename
    if (try(file_content.engine, null) == "composer")
  ]
}