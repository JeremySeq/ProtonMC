import styles from './Overview.module.css';
import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import API_SERVER from '../Constants';
import { getAuthHeader } from '../AuthorizationHelper';
import { useNotification } from '../NotificationContext';

function Overview() {

    const [serverStatus, setServerStatus] = useState(false);
    const [serverOperationalStatus, setServerOperationalStatus] = useState(false);
    const [serverStartTime, setServerStartTime] = useState(false);
    const [serverUptime, setServerUptime] = useState(false);
    const [playerList, setPlayerList] = useState([]);

    const { serverName } = useParams();
    const navigate = useNavigate();
    const { addNotification } = useNotification();

    async function queryStatus() {
        const response = await fetch(API_SERVER + "/api/servers/" + serverName + "/status", {
            headers: getAuthHeader()
        });
        const serverStatusResponse = await response.json();
        if (response.status == 200) {
            if (serverStatus && !(serverOperationalStatus)) {
                if (serverStatusResponse["message"][0] && serverStatusResponse["message"][1]) {
                    addNotification("Server has been turned on successfully", "success");
                } else if (!serverStatusResponse["message"][0]) {
                    addNotification("Server failed to start", "error");
                }
            }
            if (!serverStatusResponse["message"][0]) {
                setServerStartTime(false);
                setServerUptime(false);
            }
            setServerStatus(serverStatusResponse["message"][0]);
            setServerOperationalStatus(serverStatusResponse["message"][1]);
            return serverStatusResponse["message"][0];
        } else if (response.status == 401) {
            navigate("/login");
        } else {
            console.log("Error")
        }
    }

    async function updateServerStartTime() {
        const response = await fetch(API_SERVER + "/api/servers/" + serverName + "/status/startTime", {
            method: "GET",
            headers: getAuthHeader()
        });
        const serverStartTimeResponse = await response.json();
        if (response.status == 200) {
            setServerStartTime(serverStartTimeResponse["message"]);
        } else if (response.status == 401) {
            alert("You are not logged in.")
        } else {
            console.log("Error")
        }
    }

    async function updatePlayersOnline() {
        const response = await fetch(API_SERVER + "/api/servers/" + serverName + "/status/players", {
            method: "GET",
            headers: getAuthHeader()
        });
        const playersOnlineResponse = await response.json();
        if (response.status == 200) {
            setPlayerList(playersOnlineResponse["players"]);
        } else if (response.status == 401) {
            alert("You are not logged in.")
        } else {
            console.log("Error")
        }
    }

    async function startServer() {
        const response = await fetch(API_SERVER + "/api/servers/" + serverName + "/start", {
            method: "POST",
            headers: getAuthHeader()
        });
        if (response.status == 200) {
            queryStatus();
            updateServerStartTime();
        } else if (response.status == 401) {
            alert("You are not logged in.")
        } else {
            console.log("Error")
        }
    }

    async function stopServer() {
        const response = await fetch(API_SERVER + "/api/servers/" + serverName + "/stop", {
            method: "POST",
            headers: getAuthHeader()
        });
        if (response.status == 200) {
            queryStatus();
        } else if (response.status == 401) {
            alert("You are not logged in.")
        } else {
            console.log("Error")
        }
    }

    function clickStatusButton() {
        if (serverStatus) {
            stopServer();
        } else {
            startServer();
        }
    }

    // query status at intervals
    useEffect(() => {
        const interval = setInterval(() => {
            queryStatus();
        }, 2500);
 
        return () => clearInterval(interval);
    }, [serverStatus, serverOperationalStatus]);

    useEffect(() => {
        const interval = setInterval(() => {
            if (serverStatus) {
                updatePlayersOnline();
            } else {
                setPlayerList([]);
            }
        }, 3500);
        return () => clearInterval(interval);
    }, [serverStatus, playerList]);


    // query status on load
    useEffect(() => {
        queryStatus();
        updateServerStartTime();
        calculateServerUptime();
    }, 
    []);

    function getStatusBadgeHTML() {
        // process on but not operational: starting
        if (serverStatus && !serverOperationalStatus) {
            return <div className={`${styles.badge} ${styles.badgeStarting}`}>SERVER STARTING</div>
        } else if (serverStatus) { // process on and operational
            return <div className={`${styles.badge} ${styles.badgeOn}`}>SERVER ON</div>
        } else { // process off
            return <div className={`${styles.badge} ${styles.badgeOff}`}>SERVER OFF</div>
        }
    }

    function calculateServerUptime() {
        if (serverStartTime) {
            var currentTime = Date.now()/1000;
            setServerUptime(Math.round(currentTime-serverStartTime));
        } else {
            setServerUptime(false);
        }
    }

    useEffect(() => {
        const interval = setInterval(() => {
            calculateServerUptime();
        }, 1000);
        return () => clearInterval(interval);
    }, [serverStartTime, serverUptime]);

    function getServerUptimeHTML() {
        if (serverStatus) {
            if (serverUptime) {
                var date = new Date(serverUptime * 1000);
                return <p>{date.toISOString().substring(11, 19)}</p>
            }
            else {
                return <p>...</p>
            }
        } else {
            return <p><br></br></p>
        }
    }

    return (
        <>
            <div className={styles.container}>
                {/* <div className={`${styles.card} ${styles.spanCard}`}>
                    <h2 className={styles.serverAddress}>jeremyseq.serveminecraft.net:25565</h2>
                    <p className={styles.copyAddressButton}><i>Click to copy</i></p>
                </div> */}

                <div className={styles.card}>

                    <h2>Server Status</h2>

                    {getServerUptimeHTML()}

                    <button className={`${styles.statusButton} ${serverStatus ? styles.statusButtonOn : styles.statusButtonOff}`} onClick={() => clickStatusButton()}>
                        {serverStatus ? 
                            <i className="fa-solid fa-pause"></i>
                             : 
                            <i className="fa-solid fa-play"></i>
                        }
                    </button>
                    
                    {getStatusBadgeHTML()}
                </div>

                <div className={styles.card}>

                    <h2>Players</h2>
                    <p>{playerList.length === 0 ? "No players online" : `${playerList.length} players online`}</p>
                    
                    <div className={styles.playerList}>
                        
                        {playerList.length === 0 ? <h3 class={styles.noPlayers}><i className="fa-solid fa-users-slash"></i></h3> : ""}

                        {playerList.map(player => (
                            <div className={styles.playerElement}>
                                <img class={styles.playerImg} src={`https://minotar.net/helm/${player}/100.png`} alt=""></img>
                                <p>{player}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </>
    );
}

export default Overview;