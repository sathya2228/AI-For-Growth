"use client";

import { useState, FormEvent } from "react";
import { CornerDownLeft } from "lucide-react";
import { Button } from "./chatbot/button";
import {
  ChatBubble,
  ChatBubbleAvatar,
  ChatBubbleMessage,
} from "./chatbot/chat-bubble";
import { ChatMessageList } from "./chatbot/chat-message-list";
import { ChatInput } from "./chatbot/chat-input";
import { HyperText } from "./chatbot/Title";
import { PulsatingButton } from "./ui/button"
import { useNavigate } from 'react-router-dom';  // ✅ Import navigation hook
import axios from "axios";  // ✅ Import axios for API call


export function ChatMessageListDemo() {

  const navigate = useNavigate();  // ✅ Initialize navigation

  const handleNavigate = () => {
    navigate('/');  // ✅ Navigate to /chat page on button click

  }
  const [messages, setMessages] = useState([
    {
      id: 1,
      content: "Hello! Welcome to AI For Growth!?",
      sender: "ai",
    }
  ]);

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  // ✅ Function to handle message submission
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user's message to the chat
    setMessages((prev) => [
      ...prev,
      {
        id: prev.length + 1,
        content: input,
        sender: "user",
      },
    ]);

    setInput("");
    setIsLoading(true);

    try {
      // ✅ API call to Django backend
      const response = await axios.post("http://127.0.0.1:8000/api/chat/", {
        query: input,   // Send user input as query
      });

      // ✅ Add AI response to the chat
      setMessages((prev) => [
        ...prev,
        {
          id: prev.length + 1,
          content: response.data.answer,  // Display AI response
          sender: "ai",
        },
      ]);

    } catch (error) {
      console.error("Error:", error);

      // Display error message in chat
      setMessages((prev) => [
        ...prev,
        {
          id: prev.length + 1,
          content: "Failed to fetch response. Please try again.",
          sender: "ai",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };


  return (
  <div className="w-[950px] h-[500px] max-w-full max-h-screen border bg-background rounded-lg flex flex-col p-6 ">
    <HyperText>AI For Growth</HyperText>
                        {/* Try Now Button */}
                        <PulsatingButton
            onClick={handleNavigate}  // ✅ Navigate on click
            className="relative bg-white text-white font-bold py-30 w-20  h-3 rounded-lg 
            shadow-lg transition-transform transform hover:scale-120 
            before:absolute before:inset-0 before:rounded-lg 
            before:bg-white before:opacity-0 before:animate-pulse"
          >
            Back
          </PulsatingButton>
      <div className="flex-1 overflow-hidden">
        <ChatMessageList>
          {messages.map((message) => (
            <ChatBubble
              key={message.id}
              variant={message.sender === "user" ? "sent" : "received"}
            >
              <ChatBubbleAvatar
                className="h-8 w-8 shrink-0"
                src={
                  message.sender === "user"
                    ? "https://cdn.iconscout.com/icon/premium/png-512-thumb/human-4688769-3883119.png?f=webp&w=512"
                    : "https://cdn.iconscout.com/icon/premium/png-512-thumb/chatbot-3135112-2613085.png?f=webp&w=512"
                }
                fallback={message.sender === "user" ? "US" : "AI"}
              />
              <ChatBubbleMessage
                variant={message.sender === "user" ? "sent" : "received"}
              >
                {message.content}
              </ChatBubbleMessage>
            </ChatBubble>
          ))}

          {isLoading && (
            <ChatBubble variant="received">
              <ChatBubbleAvatar
                className="h-8 w-8 shrink-0"
                src="https://cdn.iconscout.com/icon/premium/png-512-thumb/chatbot-3135112-2613085.png?f=webp&w=512"
                fallback="AI"
              />
              <ChatBubbleMessage isLoading />
            </ChatBubble>
          )}
        </ChatMessageList>
      </div>

      <div className="p-4 border-t">
        <form
          onSubmit={handleSubmit}
          className="relative rounded-lg border bg-background focus-within:ring-1 focus-within:ring-ring p-1"
        >
          <ChatInput
            value={input}
            onChange={(e) => setInput(e.target.value)}
            // ✅ Handle "Enter" key press to submit the form
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();   // Prevents a newline in the input field
                handleSubmit(e);      // Trigger the form submission
              }
            }}
            placeholder="Type your message..."
            className="min-h-12 resize-none rounded-lg bg-background border-0 p-2 shadow-none focus-visible:ring-0 h-15"
          />
              <div className="flex items-center justify-center p-3 pt-3"> 
              <Button type="submit" size="sm" className="ml-auto gap-1.5">
              Send Message
              <CornerDownLeft className="size-3.5" />
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
