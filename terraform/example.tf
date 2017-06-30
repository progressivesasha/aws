provider "aws" {
  access_key = "${var.access_key}"
  secret_key = "${var.secret_key}"
  region = "us-east-1"
}

resource "aws_instance" "example" {
  ami = "ami-2d39803a"
  instance_type = "t2.micro"
  user_data = <<-EOF
			  #!/bin/bash
			  echo "hello 1" > index.html
			  nohup busybox httpd -f -p "${var.server_port}" &
			  EOF
  tags {
	Name="node1"
  }
  vpc_security_group_ids = ["${aws_security_group.instance.id}"]
}

resource "aws_eip" "ip" {
  instance   = "${aws_instance.example.id}"
  depends_on = ["aws_instance.example"]
}
