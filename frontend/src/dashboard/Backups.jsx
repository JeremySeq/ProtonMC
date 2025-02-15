import { useState, useEffect, useRef } from 'react';
import {useNavigate, useParams} from 'react-router-dom';
import styles from './Backups.module.css';
import API_SERVER from '../Constants';
import { getAuthHeader } from '../AuthorizationHelper';
import { useNotification } from '../NotificationContext';

function Backups() {

    const [backupList, setBackupList] = useState([]);
    const [selectedBackup, setSelectedBackup] = useState(null);
    const [backupProgress, setBackupProgress] = useState(0);
    const [backupInProgress, setBackupInProgress] = useState(false);

    const { addNotification } = useNotification();
    const { serverName } = useParams();
    const navigate = useNavigate();

    async function updateBackupList() {
        const response = await fetch(API_SERVER + "/api/servers/" + serverName + "/backup", {
            headers: getAuthHeader(),
            method: 'GET'
        });
        const backupListResponse = await response.json();
        if (response.status == 200) {
            setBackupList(backupListResponse);
        } else if (response.status == 401) {
            navigate("/login")
        } else {
            console.log("Error")
        }
    }

    function selectBackup(backup) {
        if (selectedBackup === backup) {
            setSelectedBackup(null);
        } else {
            setSelectedBackup(backup);
        }
    }

    async function startBackup() {
        if (backupInProgress) {
            addNotification("Backup is already in progress.", "warning")
        }
        const response = await fetch(API_SERVER + "/api/servers/" + serverName + "/backup", {
            headers: getAuthHeader(),
            method: 'POST'
        });
        const backupListResponse = await response.json();
        if (response.status == 200) {
            setBackupInProgress(true);
        } else if (response.status == 401) {
            navigate("/login")
        } else {
            console.log("Error")
        }
    }

    async function updateBackupProgress() {
        const response = await fetch(API_SERVER + "/api/servers/" + serverName + "/backup/progress", {
            headers: getAuthHeader(),
            method: 'GET'
        });
        const backupProgressResponse = await response.json();
        if (response.status == 200) {
            if (backupProgressResponse["isBackupping"]) {
                setBackupInProgress(true);
                setBackupProgress(backupProgressResponse["backupProgress"]);
            } else {
                if (backupInProgress) {
                    addNotification("Backup completed.", "success");
                    updateBackupList();
                }
                setBackupInProgress(false);
                setBackupProgress(0);
            }
        } else if (response.status == 401) {
            navigate("/login")
        } else {
            console.log("Error")
        }
    }
    

    // updates backup progress every second when a backup is in progress
    useEffect(() => {
        const interval = setInterval(() => {
            if (backupInProgress) {
                updateBackupProgress();
            }
        }, 1000);
 
        return () => clearInterval(interval);
    }, [backupProgress, backupInProgress]);

    // updates backup progress every 5 seconds when a backup is not in progress
    useEffect(() => {
        const interval = setInterval(() => {
            if (!backupInProgress) {
                updateBackupProgress();
            }
        }, 5000);
        return () => clearInterval(interval);
    }, [backupProgress]);

    useEffect(() => {
        updateBackupList();
        updateBackupProgress();
    }, []);

    return (
        <div className={styles.backupsContainer}>
            <ul className={styles.backupList}>
                {backupList.map((backupListItem) => (
                    <li key={backupListItem} 
                    className={`${styles.backupListItem} ${selectedBackup === backupListItem ? styles.selectedBackupListItem : ""}`} 
                    onClick={() => selectBackup(backupListItem)}>{backupListItem}</li>
                ))}
            </ul>

            <button className={styles.backupButton} onClick={startBackup}>Start Backup</button>


            <div className={styles.backupProgress} style={{display: backupInProgress ? "block" : "none"}}>
                <h3>Backup in progress... {Math.round(backupProgress)}%</h3>
                <div className={styles.backupProgressBarBorder}>
                    <div className={styles.backupProgressBar} style={{width: `${backupProgress}%`}}></div>
                </div>
            </div>
            
        </div>

        
    );
}

export default Backups;