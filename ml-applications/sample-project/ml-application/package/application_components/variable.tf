variable "region_identifier" {
  description = "Region Identifier (Implicit variable - value provided by ML Application Service)"
  type = string
}

variable "app" {
  description = "Object containing information about ML Application resource (Implicit variable - value provided by ML Application Service)"
  type = any
}

variable "app_impl" {
  description = "Object containing information about ML Application Implementation resource (Implicit variable - value provided by ML Application Service)"
  type = any
}
