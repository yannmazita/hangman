variable "aws_region" {
    description = "AWS region"
    default = "eu-west-3"
}

variable "aws_ami" {
    description = "AWS AMI ID"
    default = "ami-00c71bd4d220aa22a"
}

variable "aws_instance_type" {
    description = "AWS instance type"
    default = "t2.micro"
} 

variable "aws_key_name" {
    description = "AWS key pair name"
}

variable "aws_ssh_user" {
    description = "AWS SSH user"
}

variable "aws_private_key_path" {
    description = "AWS private key path"
}
