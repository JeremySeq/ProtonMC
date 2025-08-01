import {useEffect, useState} from 'react';
import styles from './ServerMenu.module.css';
import {getAuthHeader, getUsername, logout, userHasPermissionTo} from './AuthorizationHelper.jsx';
import API_SERVER from './Constants.jsx'
import { useNavigate } from "react-router-dom";

function ServerMenu() {

    const [serverHTML, setServerHTML] = useState('');
    const [serverCreationPermissions, setServerCreationPermissions] = useState(false);
    const [deleteServerPopup, setDeleteServerPopup] = useState(false);
    const [confirmDeletionInput, setConfirmDeletionInput] = useState('');
    const [finalDeleteButtonEnabled, setFinalDeleteButtonEnabled] = useState(false);
    const [showUserProfile, setshowUserProfile] = useState(false);
    const navigate = useNavigate();

    function goToServer(serverName) {
        console.log("Go to server " + serverName)
        navigate("/servers/" + serverName + "/overview");
    }

    function openDeleteServerPopup(serverName) {
        setDeleteServerPopup(serverName)
    }

    function getServerTags(server) {
        return <>
            <span className={styles.serverTag}>{server["type"]}</span>
            <span className={styles.serverTag}>{server["game_version"]}</span>
        </>
    }

    const updateServers = async () => {
        const response = await fetch(API_SERVER + "/api/servers/", {
            headers: getAuthHeader()
        });
        const serverList = await response.json();
        if (response.status === 200) {
            const listItems = serverList.map(server => {
                let serverClass = '';
                let content = (
                    <td onClick={() => goToServer(server["name"])}>
                        <i className="fa-solid fa-server"></i>{server["name"]} {getServerTags(server)}
                        <i className="fa-solid fa-circle"></i>
                    </td>
                );

                switch (server["status"]) {
                    case 3:
                        serverClass = styles.inaccessibleServer;
                        content = (
                            <td>
                                <i className="fa-solid fa-server"></i>{server["name"]} - Creating...
                                <div className={styles.loader}></div>
                            </td>
                        );
                        break;
                    case 2:
                        serverClass = styles.runningServer;
                        break;
                    case 1:
                        serverClass = styles.startingServer;
                        break;
                    default:
                        serverClass = styles.stoppedServer;
                        if (serverCreationPermissions) {
                            return (
                                <tr key={server["name"]} className={serverClass}>
                                    {content}
                                    <td className={styles.deleteButton}>
                                        <button onClick={() => openDeleteServerPopup(server["name"])}>
                                            <i className="fa-solid fa-trash"></i>
                                        </button>
                                    </td>
                                </tr>
                            );
                        }
                }

                return (
                    <tr key={server["name"]} className={serverClass}>
                        {content}
                    </tr>
                );
            });

            setServerHTML(listItems);
        } else if (response.status === 401) {
            navigate("/login");
            // navigate("/login")
        } else {
            console.log("Error")
        }
    };

    useEffect(() => {
        const interval = setInterval(() => {
            updateServers();
        }, 2500);

        return () => clearInterval(interval);
    }, [serverCreationPermissions]);

    useEffect(() => {
        updateServerCreationPermissions();
        updateServers();
    }, [serverCreationPermissions]);

    async function updateServerCreationPermissions() {
        const perm = await userHasPermissionTo("create_server");
        setServerCreationPermissions(perm);
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
            <div className={styles.userProfile}>
                <div className={styles.username} onClick={() => setshowUserProfile(!showUserProfile)}>{getUsername()}</div>
                {/*{showUserProfile ? <div className={styles.userProfileDropdown}>*/}
                {/*    <button>Logout</button>*/}
                {/*</div> : ""}*/}
                <div className={styles.userProfileDropdown} style={showUserProfile ? {visibility: "visible", opacity: "100%"} : {visibility: "hidden", opacity: "0%"}}>
                    <button onClick={() => {
                        logout().then(() => navigate("/login"))
                    }}>Logout</button>
                </div>
            </div>
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