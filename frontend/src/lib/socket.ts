import { io, Socket } from "socket.io-client";

const WS_BASE = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws";

let socket: Socket | null = null;

export function getSocket(): Socket {
  if (!socket) {
    socket = io(WS_BASE, {
      transports: ["websocket"],
      autoConnect: false,
    });
  }
  return socket;
}
