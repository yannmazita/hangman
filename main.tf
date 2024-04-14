terraform {
    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "~> 4.0"
        }
    }
}

provider "aws" {
    region = var.aws_region
}

resource "aws_instance" "hangman" {
    ami           = var.aws_ami
    instance_type = var.aws_instance_type
    key_name      = var.aws_key_name


    connection {
        type        = "ssh"
        user        = "var.aws_ssh_user"
        private_key = file(var.aws_private_key_path)
        #host        = aws_instance.hangman.public_ip
        host       = self.public_ip
    }

    provisioner "file" {
        source      = "docker-compose.yaml"
        destination = "/home/${var.aws_ssh_user}/docker-compose.yaml"
    }
    
    provisioner "remote-exec" {
        inline = [
            "sudo apt-get update",
            "sudo apt-get install -y docker.io docker-compose",
            "sudo docker-compose up -d"
        ]
    }
}
