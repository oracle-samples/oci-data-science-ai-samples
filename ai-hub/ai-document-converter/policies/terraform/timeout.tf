// Timeout to make sure the network is complete before start creating the containers
resource "time_sleep" "wait_seconds" {
  create_duration = "150s"
}