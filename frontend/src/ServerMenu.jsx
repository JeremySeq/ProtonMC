import { useEffect, useState } from 'react';
import reactLogo from './assets/react.svg';
import viteLogo from '/vite.svg';
import styles from './ServerMenu.module.css';
import {getAuthHeader, getUserPermissionLevel} from './AuthorizationHelper.jsx';
import API_SERVER from './Constants.jsx'
import { useNavigate } from "react-router-dom";
import ServerCreator from "./ServerCreator.jsx";

function ServerMenu() {

    const [serverHTML, setServerHTML] = useState('');
    const [createServerButton, setCreateServerButton] = useState(false);
    const navigate = useNavigate();

    function goToServer(serverName) {
        console.log("Go to server " + serverName)
        navigate("/servers/" + serverName + "/overview");
    }

    const updateServers = async () => {
        const response = await fetch(API_SERVER + "/api/servers/", {
            headers: getAuthHeader()
        });
        const serverList = await response.json();
        if (response.status == 200) {
            const listItems = serverList.map(server => {
                    if (server["status"] === 3) {
                        return <tr className={styles.inaccessibleServer}>
                            <td><i className="fa-solid fa-server"></i>{server["name"]} - Creating...</td>
                        </tr>
                    } else if (server["status"] === 2) {
                        return <tr className={styles.runningServer} onClick={() => goToServer(server["name"])}>
                            <td><i className="fa-solid fa-server"></i>{server["name"]}</td>
                        </tr>
                    } else if (server["status"] === 1) {
                        return <tr className={styles.startingServer} onClick={() => goToServer(server["name"])}>
                            <td><i className="fa-solid fa-server"></i>{server["name"]}</td>
                        </tr>
                    }
                    return <tr className={styles.stoppedServer} onClick={() => goToServer(server["name"])}>
                        <td><i className="fa-solid fa-server"></i>{server["name"]}</td>
                    </tr>
                }
            );
            setServerHTML(listItems);
        } else if (response.status == 401) {
            navigate("/login");
            // alert("You are not logged in.")
        } else {
            console.log("Error")
        }
    };

    useEffect(() => {
        const interval = setInterval(() => {
            updateServers();
        }, 2500);

        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        updateServers();
        updateButton();
    }, []);

    async function updateButton() {
        var permLevel = await getUserPermissionLevel();
        if (permLevel >= 5) {
            setCreateServerButton(true);
        } else {
            setCreateServerButton(false);
        }
    }

    function openServerCreator() {
        navigate("/create");
    }

    return (
        <>
            <h1 className={styles.pageTitle}>Servers</h1>
            <table className={styles.serverTable}>
                {serverHTML}
            </table>
            {createServerButton ? <button onClick={openServerCreator} className={styles.addServerBtn}> + </button> : ""}
        </>
    )
}

export default ServerMenu