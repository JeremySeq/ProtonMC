import { useParams, Outlet, useNavigate, Link, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import API_SERVER from "../Constants";
import {getAuthHeader} from "../AuthorizationHelper";
import styles from "./Dashboard.module.css";
import Navigation from "./Navigation.jsx";
import isMobile from "./useIsMobile.js";

function Dashboard() {
    const [sidebarOpen, setSidebarOpen] = useState(true);
    const [modsEnabled, setModsEnabled] = useState(false);
    const [pluginsEnabled, setPluginsEnabled] = useState(false);

    const { serverName } = useParams();
    const navigate = useNavigate();
    const location = useLocation();
    const mobile = isMobile();

    function isSidebarOpen() {
        return sidebarOpen && !mobile;
    }

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
        { path: `/servers/${serverName}/console`, label: "Console", icon: "fa-solid fa-terminal" },
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

                <div className={styles.centerNavbar}>
                    <img className={styles.logo} src="/assets/logo.svg" alt="logo"/>
                    <h2 className={styles.brand}>ProtonMC</h2>
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

            {<Navigation serverName={serverName} sidebarLinks={sidebarLinks} sidebarOpen={isSidebarOpen()} />}


            <div className={`${styles.content} ${isSidebarOpen() ? styles.contentShift : ''}`}>
                <Outlet />
            </div>
        </>
    );
}

export default Dashboard;
