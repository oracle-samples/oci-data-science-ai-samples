# dummy model artifact (zip) built from inline files
data "archive_file" "model_zip" {
  type        = "zip"
  output_path = "${path.module}/model-artifact.zip"

  # minimal runtime.yaml expected by OCI model artifacts
  source {
    filename = "runtime.yaml"
    content  = <<-YAML
      kind: generic
      type: python
      entryPoint: "score.py"
      pythonVersion: "3.11"
    YAML
  }

  # Trivial scorer stub
  source {
    filename = "score.py"
    content  = <<-PY
      def predict(data):
          # no-op dummy implementation
          return {"ok": True, "echo": data}
    PY
  }
}

# dummy Model catalog entry with artifact
resource "oci_datascience_model" "ai_model" {
  compartment_id = var.data_science_project_compartment_id
  project_id     = var.project_ocid
  display_name   = var.model_display_name
  description    = local.model_desc

  # Upload artifact inline (ZIP created above)
  model_artifact               = data.archive_file.model_zip.output_path
  artifact_content_length      = data.archive_file.model_zip.output_size
  artifact_content_disposition = "attachment; filename=model-artifact.zip"

  retention_setting {
    archive_after_days = 365
  }
}
