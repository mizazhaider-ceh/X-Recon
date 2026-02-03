# --- WebSocket for AI Chat ---

@app.websocket("/ws/ai")
async def websocket_ai(websocket: WebSocket):
    await websocket.accept()
    
    if not ai_client:
        await websocket.send_text("Error: Cerebras API Key not configured. Please check .env file.")
        await websocket.close()
        return

    # Enhanced system prompt matching CLI assistant
    system_instruction = (
        "You are X-AI, an elite cybersecurity assistant for the 'X-Recon' toolkit, created by Muhammad Izaz Haider. "
        "You MUST follow these formatting rules: \n"
        "1. **Spacing:** Insert a blank line between paragraphs. \n"
        "2. **Commands:** Prefix terminal commands with `Command:` (e.g., Command: nmap -A target). \n"
        "3. **Code:** Use markdown code blocks. \n"
        "4. **Signature:** End every response with: `--- \n*Created by Muhammad Izaz Haider*`\n"
        "5. **Knowledge:** You know that Muhammad Izaz Haider is a cybersecurity expert and researcher with expertise in network security, "
        "penetration testing, vulnerability assessment, AI, and software development. He created X-Recon to help cybersecurity professionals."
    )

    history = [
        {"role": "system", "content": system_instruction}
    ]

    try:
        while True:
            user_input = await websocket.receive_text()
            
            # Add user message to history
            history.append({"role": "user", "content": user_input})
            
            # Stream response
            stream = ai_client.chat.completions.create(
                messages=history,
                model="llama-3.3-70b",
                stream=True,
                temperature=0.7,
                max_tokens=1024
            )
            
            full_response = ""
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    full_response += content
                    await websocket.send_text(content)
            
            # Signal end of response
            await websocket.send_text("[END]")
            
            # Save assistant response to history
            history.append({"role": "assistant", "content": full_response})
            
    except Exception as e:
        print(f"AI WebSocket Error: {e}")
