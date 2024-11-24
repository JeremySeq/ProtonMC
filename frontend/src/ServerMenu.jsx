import {useEffect, useState} from 'react';
import styles from './ServerMenu.module.css';
import {getAuthHeader, getUserPermissionLevel} from './AuthorizationHelper.jsx';
import API_SERVER from './Constants.jsx'
import { useNavigate } from "react-router-dom";

function ServerMenu() {

    const [serverHTML, setServerHTML] = useState('');
    const [serverCreationPermissions, setServerCreationPermissions] = useState(false);
    const [deleteServerPopup, setDeleteServerPopup] = useState(false);
    const [confirmDeletionInput, setConfirmDeletionInput] = useState('');
    const [finalDeleteButtonEnabled, setFinalDeleteButtonEnabled] = useState(false);
    const navigate = useNavigate();

    function goToServer(serverName) {
        console.log("Go to server " + serverName)
        navigate("/servers/" + serverName + "/overview");
    }

    function openDeleteServerPopup(serverName) {
        setDeleteServerPopup(serverName)
    }

    const updateServers = async () => {
        const response = await fetch(API_SERVER + "/api/servers/", {
            headers: getAuthHeader()
        });
        const serverList = await response.json();
        if (response.status === 200) {
            const listItems = serverList.map(server => {
                    if (server["status"] === 3) {
                        return <tr key={server["name"]} className={styles.inaccessibleServer}>
                            <td><i className="fa-solid fa-server"></i>{server["name"]} - Creating... <div className={styles.loader}></div></td>
                        </tr>
                    } else if (server["status"] === 2) {
                        return <tr key={server["name"]} className={styles.runningServer}>
                            <td onClick={() => goToServer(server["name"])}><i
                                className="fa-solid fa-server"></i>{server["name"]}<i
                                className="fa-solid fa-circle"></i></td>
                        </tr>
                    } else if (server["status"] === 1) {
                        return <tr key={server["name"]} className={styles.startingServer}>
                            <td onClick={() => goToServer(server["name"])}><i
                                className="fa-solid fa-server"></i>{server["name"]}<i
                                className="fa-solid fa-circle"></i></td>
                        </tr>
                    }

                    if (serverCreationPermissions) {
                        return <tr key={server["name"]} className={styles.stoppedServer}>
                            <td onClick={() => goToServer(server["name"])}><i
                                className="fa-solid fa-server"></i>{server["name"]}<i className="fa-solid fa-circle"></i>
                            </td>
                            <td className={styles.deleteButton}>
                                <button onClick={() => openDeleteServerPopup(server["name"])}><i
                                    className="fa-solid fa-trash"></i></button>
                            </td>
                        </tr>
                    }
                    return <tr key={server["name"]} className={styles.stoppedServer}>
                        <td onClick={() => goToServer(server["name"])}><i
                            className="fa-solid fa-server"></i>{server["name"]}<i className="fa-solid fa-circle"></i>
                        </td>
                    </tr>
                }
            );
            setServerHTML(listItems);
        } else if (response.status === 401) {
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
        updateServerCreationPermissions();
        updateServers();
    }, [serverCreationPermissions]);

    async function updateServerCreationPermissions() {
        const permLevel = await getUserPermissionLevel();
        if (permLevel >= 5) {
            setServerCreationPermissions(true);
        } else {
            setServerCreationPermissions(false);
        }
    }

    function openServerCreator() {
        navigate("/create");
    }

    function updateConfirmDeletionInput(event) {
        setConfirmDeletionInput(event.target.value);
        if (event.target.value === deleteServerPopup) {
            setFinalDeleteButtonEnabled(true);
        } else {
            setFinalDeleteButtonEnabled(false);
        }
    }

    async function finalDeleteServer() {
        let formData = new FormData();
        if (!deleteServerPopup) {
            setDeleteServerPopup(false);
            setConfirmDeletionInput("");
            return false
        }
        formData.append("name", deleteServerPopup);
        const response = await fetch(API_SERVER + "/api/servers/", {
            method: "DELETE",
            headers: getAuthHeader(),
            body: formData
        });
        await response.json();
        if (response.status === 200) {
            console.log("Deleted server " + deleteServerPopup);
        } else {
            console.log("Error deleting server " + deleteServerPopup);
        }
        setDeleteServerPopup(false);
        setConfirmDeletionInput("");
    }

    function closeDeleteServerPopup() {
        setDeleteServerPopup(false);
        setConfirmDeletionInput("");
    }

    return (
        <>
            <h1 className={styles.pageTitle}>Servers</h1>
            <table className={styles.serverTable}>
                {serverHTML}
            </table>
            {serverCreationPermissions ? <button onClick={openServerCreator} className={styles.addServerBtn}> + </button> : ""}

            {deleteServerPopup ? <div className={styles.deleteServerPopup}>
                <h2>Delete {deleteServerPopup}
                    <button onClick={closeDeleteServerPopup}><i className="fa-solid fa-xmark"></i></button>
                </h2>
                <br></br>

                <p>To confirm, type &quot;{deleteServerPopup}&quot; in the box below</p>
                <input value={confirmDeletionInput} onChange={updateConfirmDeletionInput} type="text"/>
                <button onClick={finalDeleteServer} disabled={!finalDeleteButtonEnabled}>Delete this server</button>
            </div>: ""}
        </>
    )
}

export default ServerMenu