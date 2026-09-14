variable "project_id" {
  type = string
}

variable "region" {
  type    = string
  default = "europe-west2"
}

variable "location" {
  type    = string
  default = "EU"
}

variable "bucket_name" {
  type = string
}

variable "dataset_name" {
  type    = string
  default = "ttf_gas"
}