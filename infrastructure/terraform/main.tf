terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.5"
}

provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "my-cloud-platform"
  cidr = "10.0.0.0/16"

  azs             = [var.aws_az]
  public_subnets  = ["10.0.1.0/24"]
  private_subnets = ["10.0.2.0/24"]

  enable_nat_gateway = false
  single_nat_gateway = true
}

resource "aws_ecr_repository" "online_boutique" {
  name                 = "online-boutique"
  image_tag_mutability = "IMMUTABLE"
  force_delete         = true
}
