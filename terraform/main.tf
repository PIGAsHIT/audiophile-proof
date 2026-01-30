terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {}


resource "docker_network" "audiophile_net" {
  name = "audiophile_network"
}



resource "docker_image" "redis" {
  name         = "redis:latest"
  keep_locally = false
}

resource "docker_container" "redis" {
  image = docker_image.redis.image_id
  name  = "terraform-redis"
  
  ports {
    internal = 6379
    external = 6379
  }

  
  networks_advanced {
    name = docker_network.audiophile_net.name
  }
}



resource "docker_image" "postgres" {
  name         = "postgres:15"
  keep_locally = false
}

resource "docker_container" "postgres" {
  image = docker_image.postgres.image_id
  name  = "terraform-postgres"
  
  
  env = [
    "POSTGRES_USER=user",
    "POSTGRES_PASSWORD=password",
    "POSTGRES_DB=audiophile"
  ]
  
  ports {
    internal = 5432
    external = 5432
  }

 
  networks_advanced {
    name = docker_network.audiophile_net.name
  }
  
  
  volumes {
    host_path      = abspath("${path.cwd}/pgdata") # 會在當前目錄建立資料夾
    container_path = "/var/lib/postgresql/data"
  }
}



resource "docker_image" "mongo" {
  name         = "mongo:latest"
  keep_locally = false
}

resource "docker_container" "mongo" {
  image = docker_image.mongo.image_id
  name  = "terraform-mongo"
  
  
  env = [
    "MONGO_INITDB_ROOT_USERNAME=admin",
    "MONGO_INITDB_ROOT_PASSWORD=password"
  ]
  
  ports {
    internal = 27017
    external = 27017
  }

  
  networks_advanced {
    name = docker_network.audiophile_net.name
  }
  
  
  volumes {
    host_path      = abspath("${path.cwd}/mongodata")
    container_path = "/data/db"
  }
}
