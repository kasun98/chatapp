import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
from groq import Groq
import markdown
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from datetime import datetime

load_dotenv()

g_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=g_key)
model = genai.GenerativeModel('gemini-1.5-flash')

l_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=l_key,)

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = f"room_{self.scope['url_route']['kwargs']['room_name']}"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        self.close(code)

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        event = {"type": "send_message", "message": data_json, "sender_channel": self.channel_name}
        
        # Save the message only if this instance is the sender
        await self.create_message(data_json)
        
        await self.channel_layer.group_send(self.room_name, event)

        # Check if message contains "@gemini"
        if "@gemini" in data_json["message"].lower():
            query = data_json["message"].split("@gemini", 1)[1].strip()

            # Get response from Gemini API
            if query:
                system_message_text = await self.get_gemini_response(query)
            else:
                system_message_text = await self.get_gemini_response("Hello")

            system_message = {
                "sender": "Gemini AI",
                "message": system_message_text,
                "time": data_json["time"]
            }
            system_event = {"type": "send_system_message", "message": system_message}
            await self.channel_layer.group_send(self.room_name, system_event)

        if "@llama3" in data_json["message"].lower():
            query = data_json["message"].split("@llama3", 1)[1].strip()
            if query:
                system_message_text = await self.get_llama_response(query)
            else:
                system_message_text = await self.get_llama_response("Hello")
            system_message = {
                "sender": "Llama3 AI",
                "message": system_message_text,
                "time": data_json["time"]
            }
            system_event = {"type": "send_system_message", "message": system_message}
            await self.channel_layer.group_send(self.room_name, system_event)

    async def send_message(self, event):
        data = event["message"]
        sender_channel = event["sender_channel"]

        # Send the message to the WebSocket
        response = {"sender": data["sender"], "message": data["message"], "time": data["time"]}
        await self.send(text_data=json.dumps({"message": response}))

    @database_sync_to_async
    def create_message(self, data):

        from .models import Room, Message, User

        get_room = Room.objects.get(id=data["room_name"])
        username = User.objects.get(username=data["sender"])

        timestamp = datetime.strptime(data["time"], "%b %d, %Y, %I:%M %p").strftime("%Y-%m-%d %H:%M:%S")

        Message.objects.create(
                room=get_room, message=data["message"], sender=username, timestamp=timestamp
            )

    async def send_system_message(self, event):
        data = event["message"]
        response = {"sender": data["sender"], "message": data["message"], "time": data["time"]}
        await self.send(text_data=json.dumps({"message": response}))
    
    async def get_gemini_response(self, query):
        response = model.generate_content(query)
        html_response = markdown.markdown(response.text)
        return html_response
    
    async def get_llama_response(self, query):
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "you are a helpful assistant."},
                {"role": "user", "content": query},
            ],
            model="llama3-8b-8192",
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stop=None,
            stream=False,
        )
        response_content = chat_completion.choices[0].message.content
        html_content = markdown.markdown(response_content)
        return html_content