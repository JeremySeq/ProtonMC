import { useEffect } from "react";
import { useLocation } from "react-router-dom";
import {getSocket} from "./SocketConnection.js";

export default function RouteWatcher() {
    const location = useLocation();

    useEffect(() => {
        let pageInfo;

        if (location.pathname === "/servers/" || location.pathname === "/servers") {
            pageInfo = { page: "server_menu" };
        } else if (location.pathname.startsWith("/servers/")) {
            const server_id = location.pathname.split("/")[2];
            const dash_page = location.pathname.split("/")[3];
            pageInfo = { page: "server_dashboard", serverId: server_id, dash_page };
        } else {
            pageInfo = { page: "other", path: location.pathname };
        }

        if (getSocket() != null) {
            getSocket().emit("page_change", pageInfo);
        }
    }, [location]);

    return null;
}
