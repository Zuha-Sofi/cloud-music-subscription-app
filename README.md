Music Subscription Web Application 🎵☁️

This project is a cloud-enabled music subscription web application developed as part of RMIT University coursework. The application demonstrates a full-stack system with Python Flask backend, AWS services, and secure, scalable architecture.

🌟 Overview

Users can:

Register & log in with credentials stored in AWS DynamoDB.

Search for songs using title, artist, album, or year.

Subscribe to songs and view them in a personal library.

View artist images stored in AWS S3.

Remove songs from their subscription list.

The application architecture supports serverless event-driven operations through AWS Lambda and API Gateway, while the frontend can be hosted on AWS EC2 or locally.

🔧 Tools & Technologies Used

AWS DynamoDB → Stores user credentials, music metadata, and subscriptions.

AWS S3 →  storage for artist images.

AWS Lambda → Serverless functions for CRUD operations.

AWS API Gateway → Handles requests from frontend to Lambda functions.

Flask (Python) → Backend web framework.

HTML, CSS, JavaScript → Frontend UI.

Other Tools → JSON dataset for music, session management, and environment variable configuration.

🚀 Features

User Authentication

Unique email registration.

Login validation using DynamoDB credentials.

Music Management

Query songs by title, artist, album, or year.

Subscribe/unsubscribe songs stored in DynamoDB.

Media Management

Artist images can be rendered from S3 URLs.

Frontend dynamically updates subscription library.

Scalable Architecture

Lambda functions handle database operations.

RESTful APIs via API Gateway.

Compatible with EC2 deployment for public access.
