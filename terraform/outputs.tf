output "bucket_name" {
  value = google_storage_bucket.lake.name
}

output "dataset_id" {
  value = google_bigquery_dataset.ttf_gas.dataset_id
}