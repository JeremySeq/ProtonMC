import { Outlet } from "react-router-dom";
import RouteWatcher from "./RouteWatcher.jsx";

export default function AppLayout() {
    return (
        <>
            <RouteWatcher />
            <Outlet />
        </>
    );
}
