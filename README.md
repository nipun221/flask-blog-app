# DevOps Project Report: Automated CI/CD Pipeline for a 2-Tier Flask Blog Application on AWS

### Author: Nipun Vats
### Date: November 2025
### Video Demo: https://youtu.be/1EkM6_5L7xc

---

## 📑 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture Diagram](#2-architecture-diagram)
3. [Step 1: AWS EC2 Instance Preparation](#3-step-1-aws-ec2-instance-preparation)
4. [Step 2: Install Dependencies on EC2](#4-step-2-install-dependencies-on-ec2)
5. [Step 3: Jenkins Installation and Setup](#5-step-3-jenkins-installation-and-setup)
6. [Step 4: GitHub + 2-Tier Flask Project Setup](#6-step-4-github--2tier-flask-project-setup)

   * [Dockerfile](#dockerfile)
   * [docker-compose.yml](#docker-composeyml)
   * [Jenkinsfile](#jenkinsfile)
7. [Step 5: Jenkins Pipeline Creation and GitHub Webhook Trigger](#7-step-5-jenkins-pipeline--webhook-trigger)
8. [Conclusion](#8-conclusion)

---

## **1. Project Overview**

This project demonstrates a complete **DevOps CI/CD pipeline** for deploying a **2-tier Flask Blog Application** on AWS.
The architecture consists of:

* **Flask (Python) Web Application** – User signup, login, and posting blogs
* **MySQL Database** – Stores users & posts
* **Docker & Docker Compose** – Containerized multi-service deployment
* **Jenkins Pipeline** – Automates build & deployment
* **GitHub Webhooks** – Automatically triggers builds on `git push`
* **AWS EC2** – Acts as Jenkins host + Application deployment server

Whenever code is pushed to the main branch, Jenkins builds the Docker image and redeploys the updated 2-tier application automatically.

---

## **2. Architecture Diagram**

```
Developer --> GitHub Repo --> Jenkins on EC2 --> Docker Compose --> Flask + MySQL App
```

```
+-----------------+      +----------------------+      +-----------------------------+
|   Developer     |----->|     GitHub Repo      |----->|        Jenkins Server       |
| (Pushes Code)   |      | (Source Code Mgmt)   |      |   (AWS EC2 Instance)        |
+-----------------+      +----------------------+      |                             |
                                                       | 1. Pull latest code         |
                                                       | 2. Build Docker image        |
                                                       | 3. Deploy with Compose       |
                                                       +--------------+--------------+
                                                                      |
                                                                      v
                                                       +-----------------------------+
                                                       |   2-Tier Flask Application  |
                                                       |     (on same EC2 server)    |
                                                       |                             |
                                                       |  Flask Container (Port 5000) |
                                                       |              |               |
                                                       |              v               |
                                                       |  MySQL Container (Port 3306)|
                                                       +-----------------------------+
```

---

## **3. Step 1: AWS EC2 Instance Preparation**

### **Launch EC2 Instance**

* AMI: **Ubuntu 22.04 LTS**
* Type: **t2.micro**
* Create & download SSH key
* Configure Security Group:

| Port | Purpose          |
| ---- | ---------------- |
| 22   | SSH              |
| 8080 | Jenkins          |
| 5000 | Flask App        |
| 3306 | MySQL (optional) |
| 80   | HTTP (optional)  |

### **Connect via SSH**

```bash
ssh -i key.pem ubuntu@<EC2-PUBLIC-IP>
```

---

## **4. Step 2: Install Dependencies on EC2**

### **Update server**

```bash
sudo apt update && sudo apt upgrade -y
```

### **Install Git, Docker & Compose**

```bash
sudo apt install git docker.io docker-compose-v2 -y
```

### **Start & enable Docker**

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### **Give Docker rights to the user**

```bash
sudo usermod -aG docker $USER
newgrp docker
```

---

## **5. Step 3: Jenkins Installation and Setup**

### **Install Java**

```bash
sudo apt install openjdk-17-jdk -y
```

### **Install Jenkins**

```bash
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key \
| sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null

echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
https://pkg.jenkins.io/debian-stable binary/ \
| sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null

sudo apt update
sudo apt install jenkins -y
```

### **Enable & start Jenkins**

```bash
sudo systemctl enable jenkins
sudo systemctl start jenkins
```

### **Give Jenkins Docker access**

```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

Access Jenkins at:

```
http://<EC2-PUBLIC-IP>:8080
```

---

## **6. Step 4: GitHub + 2-Tier Flask Project Setup**

Refer to these files: [ Dockerfile, docker-compose.yml & Jenkinsfile ] and setup accordingly.

---

## **7. Step 5: Jenkins Pipeline & Webhook Trigger**

### **Create Pipeline Job**

* Dashboard → New Item → Pipeline
* Definition: *Pipeline script from SCM*
* SCM: Git
* Script path: `Jenkinsfile`

### **Enable GitHub Webhook Trigger**

In Jenkins job:

```
Build Triggers → GitHub hook trigger for GITScm polling
```

### **Add Webhook in GitHub Repo**

GitHub → Repository → Settings → Webhooks → Add Webhook

| Field        | Value                                         |
| ------------ | --------------------------------------------- |
| Payload URL  | `http://<EC2-PUBLIC-IP>:8080/github-webhook/` |
| Content type | application/json                              |
| Events       | Just the push event                           |

### **Test**

```bash
git add .
git commit -m "Webhook test"
git push
```

A new Jenkins build will trigger automatically 🎉

---

## **8. Conclusion**

You now have a fully automated deployment pipeline:

* **Push code to GitHub**
* GitHub sends webhook → Jenkins triggers
* Jenkins pulls latest code
* Jenkins runs Docker Compose
* EC2 deploys updated Flask + MySQL app
* App available at:

  ```
  http://<EC2-PUBLIC-IP>:5000
  ```

This is a complete **CI/CD + Docker + Jenkins + AWS** production-style workflow.


