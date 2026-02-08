#   Post_Feed_API

##  Project Overview
This project is a production-grade backend system for a social media feed platform. It supports post creation, user interactions (likes, comments, shares), personalized feed generation, and real-time processing using background tasks.

The system is built with scalability, flexibility, and real-world applicability in mind, following modern backend engineering standards and best practices.

This project is part of Project Nexus, demonstrating mastery of:

Django backend architecture

GraphQL API design

Asynchronous task processing

Database optimization

Containerized deployment

CI/CD workflows

Security and testing

A backend that serves a
post feed with personalized recommendations. It stores Users, Posts  and keeps records of users. 

It returns a personalized feed for a user.

##  Technologies Used:
**Category	            **Tools
Language	            Python 3.12
Framework	            Django 5
Database	            PostgreSQL
API Layer	            GraphQL (graphene-django), REST (fallback)
Auth	                djangorestframework-simplejwt
Background Tasks	    Celery + RabbitMQ
Containerization	    Docker & Docker Compose
Documentation	        Swagger/OpenAPI, GraphQL Playground


##  Key Features
##  Post & Interaction Management

Create, retrieve, update, and soft-delete posts

Like, comment, and share posts

Track interactions for analytics and personalization

##  GraphQL API

Flexible querying of posts, users, and interactions

Custom resolvers and mutations

Hosted GraphQL Playground for testing

##  Scalable Architecture

PostgreSQL with indexing and optimized queries

Background task processing with Celery + RabbitMQ

Modular Django app structure

##  Security & Reliability

JWT authentication

Rate limiting and input validation

Unit and integration testing


##  Instructions **
### Prerequisites

Python 3.12
pip
docker
venv
PostgreSQL
Graphql

##  Local Setup Locally
1. Clone repo

2. Create virtual environment and activate it. Then install Docker in root project

3.  **To run migrations on docker** 

docker compose build web up 

docker compose up -d 

python manage.py makemigration

docker compose exec web 

python manage.py migrate

4. ###  To populate with seed data(while on docker)** 

docker compose exec web python postfeed/manage.py seed

5.  ##  Test with Graphql
Query all posts
query {
  allPosts {
    id
    text
    author {
      id
      username
    }
    tags {
      id
      name
    }
    likeCount
    commentCount
    shareCount
    comments {
      id
      text
      author {
        username
      }
    }
    createdAt
  }
}


This fetches all posts, with the author and tags, so you can see the structure of data returned by the API.”

### Query a single post with analytics
### Here’s a post along with analytics: views, likes, comments, and shares. This shows the API tracks engagement.”

query {
  postById(id: 1) {
    id
    text
    author {
      id
      username
    }
    tags {
      name
    }
    likeCount
    commentCount
    shareCount
    comments {
      id
      text
      author {
        username
      }
    }
    createdAt
  }
}

### To Create a post 

mutation {
  createPost(
    text: "This is a demo post for GraphQL"
    tagNames: ["Demo", "GraphQL"]
  ) {
    post {
      id
      text
      author {
        username
      }
      tags {
        name
      }
      createdAt
    }
  }
}

### To like a post
mutation {
  likePost(postId: 1) {
    like {
      id
      user {
        username
      }
      post {
        id
        text
      }
    }
  }
}

### For the purposes of analytics and to know the rate of likes, comment, basically take a count  we query like this:

query {
  postById(id: 1) {
    id
    text
    likeCount
    commentCount
    shareCount

