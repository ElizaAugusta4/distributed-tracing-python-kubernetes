variable "OWNER_LC" {
  default = ""
}

variable "GIT_SHA" {
  default = ""
}

group "default" {
  targets = ["catalog", "cart", "order"]
}

target "_common" {
  context = "./services"
  platforms = ["linux/amd64"]
}

target "catalog" {
  inherits = ["_common"]
  dockerfile = "./services/catalog/Dockerfile"
  tags = ["ghcr.io/${OWNER_LC}/distributed-tracing-python-kubernetes/catalog:${GIT_SHA}"]
}

target "cart" {
  inherits = ["_common"]
  dockerfile = "./services/cart/Dockerfile"
  tags = ["ghcr.io/${OWNER_LC}/distributed-tracing-python-kubernetes/cart:${GIT_SHA}"]
}

target "order" {
  inherits = ["_common"]
  dockerfile = "./services/order/Dockerfile"
  tags = ["ghcr.io/${OWNER_LC}/distributed-tracing-python-kubernetes/order:${GIT_SHA}"]
}
