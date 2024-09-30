import { useEffect, useState } from 'react';
import reactLogo from './assets/react.svg';
import viteLogo from '/vite.svg';
import styles from './ServerMenu.module.css';
import {getAuthHeader, getUserPermissionLevel} from './AuthorizationHelper.jsx';
import API_SERVER from './Constants.jsx'
import { useNavigate } from "react-router-dom";

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
            for (var i = 0; i < serverList.length; i++) {
                const listItems = serverList.map(serverName => 
                    <tr onClick={() => goToServer(serverName)}><td><i className="fa-solid fa-server"></i>{serverName}</td></tr>
                );
                setServerHTML(listItems);
            }
        } else if (response.status == 401) {
            navigate("/login");
            // alert("You are not logged in.")
        } else {
            console.log("Error")
        }
    };

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
    
    return (
        <>
            <h1 className={styles.pageTitle}>Servers</h1>
            <table className={styles.serverTable}>
                {serverHTML}
            </table>
            {createServerButton ? <button className={styles.addServerBtn}> + </button> : ""}
        </>
    )
}

export default ServerMenu