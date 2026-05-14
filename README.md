# Chat APP

A Django-based real-time chat web app where users can register, log in, chat with friends, create and manage groups, and interact with AI models in group chats.

## Features

*   **User Authentication**: Full registration and secure login functionality for all users.
*   **Private Chats**: Seamless direct messaging capabilities between friends.
*   **Group Chats**: robust group management allowing users to create groups, manage members, and exercise administrative controls (exclusive to group admins).
*   **AI Interaction**: Integrated conversational intelligence in group chats via `@gemini` or `@llama3` mentions.
*   **Real-time Communication**: Instantaneous messaging delivery powered by WebSockets.

## Technologies

### Backend & Core Logic
*   **Language**: Python
*   **Framework**: Django (with ASGI and Django Channels)
*   **Server**: Daphne
*   **Database**: PostgreSQL
*   **Caching**: Redis

### Artificial Intelligence
*   **Inference Engine**: Groq (Llama3 8B)
*   **Generative Models**: Google Generative AI

### Frontend
*   **Languages**: HTML, CSS, JavaScript
*   **Framework**: Bootstrap

### Infrastructure & Deployment
*   **Hosting**: Render Web Services (Free Tier)
