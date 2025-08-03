import { io } from "socket.io-client";
import API_SERVER from "./Constants.jsx";
import { getAuthHeader } from "./AuthorizationHelper.jsx";

let socket = null;

connectSocket();

export default function connectSocket() {
    if (socket) {
        socket.disconnect();
    }
    socket = io(API_SERVER, {
        query: getAuthHeader()
    });

    socket.on("connect", () => {
        console.log("Connected to websocket with id: " + socket.id);
    });

    return socket;
}

export function disconnectSocket() {
    if (socket) {
        socket.disconnect();
        socket = null;
    }
}

export function getSocket() {
    return socket;
}
