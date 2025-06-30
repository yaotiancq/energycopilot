import { useEffect, useRef, useState } from "react";
import type { FormEvent } from "react";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const WS_URL = "wss://a6r06wtind.execute-api.us-west-1.amazonaws.com/dev";

type Message = {
  role: "user" | "bot";
  content: string;
};

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<
    "connecting" | "connected" | "disconnected"
  >("connecting");

  const bottomRef = useRef<HTMLDivElement | null>(null);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const socket = new WebSocket(WS_URL);
    socketRef.current = socket;

    socket.onopen = () => {
      console.log("WebSocket connected");
      setConnectionStatus("connected");
    };

    socket.onmessage = (event) => {
      let token = "";
      try {
        const parsed = JSON.parse(event.data);
        token = parsed.response || "";
      } catch {
        token = event.data;
      }

      setMessages((prev) => {
        const last = prev[prev.length - 1];
        if (last?.role === "bot") {
          return [...prev.slice(0, -1), { ...last, content: last.content + token }];
        } else {
          return [...prev, { role: "bot", content: token }];
        }
      });

      setLoading(false);
    };

    socket.onerror = () => {
      setConnectionStatus("disconnected");
      setMessages((prev) => [
        ...prev,
        { role: "bot", content: "WebSocket error!" },
      ]);
      setLoading(false);
    };

    socket.onclose = () => {
      console.log("🔴 WebSocket disconnected");
      setConnectionStatus("disconnected");
    };

    return () => socket.close();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (
      !input.trim() ||
      !socketRef.current ||
      socketRef.current.readyState !== WebSocket.OPEN
    ) {
      setMessages((prev) => [
        ...prev,
        { role: "bot", content: "Cannot send message!" },
      ]);
      return;
    }

    const userMsg: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg, { role: "bot", content: "" }]);
    setLoading(true);

    socketRef.current.send(
      JSON.stringify({ action: "message", data: input })
    );
    setInput("");
  };

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      <div className="text-sm p-2 text-center">
        {connectionStatus === "connected" && (
          <span className="text-green-600">🟢 Connected</span>
        )}
        {connectionStatus === "connecting" && (
          <span className="text-yellow-600">🟡 Connecting…</span>
        )}
        {connectionStatus === "disconnected" && (
          <span className="text-red-600">🔴 Disconnected</span>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`mb-2 flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`px-4 py-2 rounded shadow w-fit max-w-[70%] ${
                msg.role === "user"
                  ? "bg-blue-100 text-blue-900 whitespace-pre-line"
                  : "bg-white"
              }`}
            >
              {msg.role === "bot" ? (
                <div className="prose break-words">
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      strong: ({ node, ...props }) => (
                        <strong className="font-semibold" {...props} />
                      ),
                      ul: ({ node, ...props }) => (
                        <ul className="list-disc pl-6 mb-2" {...props} />
                      ),
                      p: ({ node, ...props }) => (
                        <p className="mb-2 leading-relaxed" {...props} />
                      ),
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                </div>
              ) : (
                <span className="break-words whitespace-pre-line">{msg.content}</span>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="text-center text-gray-500">Waiting for response…</div>
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={sendMessage} className="flex p-4 border-t bg-white">
        <input
          className="flex-1 border rounded px-4 py-2 mr-2"
          placeholder="Please enter your question…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault(); 
              const form = e.currentTarget.form;
              if (form) {
                form.requestSubmit(); 
              }
            }
          }}
        />
        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded"
          disabled={loading}
        >
          Send
        </button>
      </form>
    </div>
  );
}

export default App;

