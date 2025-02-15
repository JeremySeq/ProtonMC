import { useParams, Outlet, useNavigate, Link, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import API_SERVER from "../Constants";
import {getAuthHeader} from "../AuthorizationHelper";
import styles from "./Dashboard.module.css";

function Dashboard() {
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [modsEnabled, setModsEnabled] = useState(false);
    const [pluginsEnabled, setPluginsEnabled] = useState(false);

    const { serverName } = useParams();
    const navigate = useNavigate();
    const location = useLocation();

    async function init() {
        const response = await fetch(`${API_SERVER}/api/servers/${serverName}`, {
            headers: getAuthHeader()
        });
        let json = await response.json();
        if (response.status === 200) {
            let type = json["type"];
            if (type === "FORGE" || type === "FABRIC" || type === "NEOFORGE") {
                setModsEnabled(true);
            } else if (type === "SPIGOT") {
                setPluginsEnabled(true);
            }
        } else if (response.status === 401) {
            navigate("/login");
        } else if (response.status === 404) {
            alert("This server does not exist.");
            navigate("/servers");
        } else {
            console.error("Error");
        }
    }

    useEffect(() => {
        init();
    }, []);

    function openSidebar() {
        setSidebarOpen(!sidebarOpen);
    }

    const sidebarLinks = [
        { path: `/servers/${serverName}/overview`, label: "Overview", icon: "fa-solid fa-house" },
        { path: `/servers/${serverName}/console`, label: "Console", icon: "fa-regular fa-file" },
        { path: `/servers/${serverName}/backups`, label: "Backups", icon: "fa-solid fa-clone" }
    ];

    if (modsEnabled) {
        sidebarLinks.push({
            path: `/servers/${serverName}/mods`,
            label: "Mods",
            icon: "fa-solid fa-puzzle-piece",
        });
    }
    if (pluginsEnabled) {
        sidebarLinks.push({
            path: `/servers/${serverName}/mods`,
            label: "Plugins",
            icon: "fa-solid fa-puzzle-piece",
        });
    }

    const navbarLinks = [
        { path: `/servers/`, label: "Servers", icon: "fa-solid fa-server" }
    ];

    function getPageFromPath() {
        var currentPath = decodeURIComponent(location.pathname);
        for (var i = 0; i < sidebarLinks.length; i++) {
            if (currentPath === sidebarLinks[i].path) {
                return sidebarLinks[i].label;
            }
        }
        return "";
    }

    const currentPath = decodeURIComponent(location.pathname);

    return (
        <>
            <div className={styles.navbar}>

                <div className={styles.leftSide}>
                    <button className={styles.openSidebarButton} onClick={openSidebar}>
                        <i className="fa-solid fa-bars"></i>
                    </button>
                    <h2 className={styles.serverName}>{serverName}</h2>
                    <h2 className={styles.pageName}> | {getPageFromPath()}</h2>
                </div>
                

                <div className={styles.rightSide}>

                    <div className={styles.navbarLinks}>
                        {navbarLinks.map((link) => (
                            <Link
                                key={link.path}
                                to={link.path}
                            >
                                <i className={link.icon}></i>
                            </Link>
                        ))}
                    </div>
                    
                </div>
            </div>

            <div
                className={`${styles.sidebar} ${sidebarOpen ? styles.sidebarOpen : ""}`}
                id="sidebar"
            >
                <div className={styles.links}>
                    {sidebarLinks.map((link) => (
                        <Link
                            key={link.path}
                            to={link.path}
                            onClick={() => setSidebarOpen(false)}
                            className={currentPath === link.path ? styles.activeLink : ""}
                        >
                            <i className={link.icon}></i>
                            {link.label}
                        </Link>
                    ))}
                </div>
            </div>

            <div className={styles.content} onClick={() => setSidebarOpen(false)}>
                <Outlet />
            </div>
        </>
    );
}

export default Dashboard;
