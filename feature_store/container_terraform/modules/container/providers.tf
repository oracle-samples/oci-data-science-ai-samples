# Copyright (c) 2024, Oracle and/or its affiliates. All rights reserved.
# Licensed under the Universal Permissive License v 1.0 as shown at http://oss.oracle.com/licenses/upl.
#

terraform {
  required_providers {
    oci = {
      source  = "hashicorp/oci"
      # https://registry.terraform.io/providers/oracle/oci/
      configuration_aliases = [oci.home_region]
    }
  }
}
