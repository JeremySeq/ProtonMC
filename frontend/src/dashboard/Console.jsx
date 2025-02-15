import { useState, useEffect } from 'react';
import {useNavigate, useParams} from 'react-router-dom';
import styles from './Console.module.css';
import API_SERVER from '../Constants';
import { getAuthHeader } from '../AuthorizationHelper';
import { useNotification } from '../NotificationContext';

function Console() {
    const [serverConsole, setServerConsole] = useState("");
    const { serverName } = useParams();

    const { addNotification } = useNotification();
    const navigate = useNavigate();

    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function addItalicsForTags(consoleStr) {
        const escapedLine = escapeHtml(consoleStr);
        return escapedLine.split('\n').map(line => {
            return line.replace(/^(\[([^\]]+)\]\s*)+/, match => {
                return match.replace(/\[([^\]]+)\]/g, '<i>[$1]</i>');
            });
        }).join('<br>');
    }

    async function updateConsole() {
        const response = await fetch(API_SERVER + "/api/servers/" + serverName + "/console", {
            headers: getAuthHeader(),
            method: 'GET'
        });
        const newServerConsoleList = await response.json();
        if (response.status === 200) {
            var newServerConsole = newServerConsoleList.join('\n');
            updateConsoleContent(addItalicsForTags(newServerConsole));
        } else if (response.status === 401) {
            navigate("/login");
        } else {
            console.log("Error");
        }
    }

    function updateConsoleContent(newContent) {
        var consoleElement = document.getElementById("console");
        var { scrollTop, scrollHeight, clientHeight } = consoleElement;

        setServerConsole(newContent);

        // auto scroll to bottom
        setTimeout(() => {
            if (scrollHeight - scrollTop >= clientHeight - 10 && scrollHeight - scrollTop <= clientHeight + 10) {
                document.getElementById("console").scrollTop = document.getElementById("console").scrollHeight;
            }
        }, 0);
    }

    useEffect(() => {
        const interval = setInterval(() => {
            updateConsole();
        }, 2500);

        return () => clearInterval(interval);
    }, [serverName]);

    useEffect(() => {
        updateConsole();
    }, []);

    async function sendCommand(command) {
        var form = new FormData();
        form.set("command", command);
        const response = await fetch(API_SERVER + "/api/servers/" + serverName + "/console", {
            headers: getAuthHeader(),
            method: 'POST',
            body: form
        });
        const commandResponse = await response.json();
        if (response.status === 200) {
            if (commandResponse["message"]) {
                setTimeout(() => updateConsole(), 50);
            } else {
                addNotification("Couldn't send command. Server is offline.", "error");
            }
        } else if (response.status === 401) {
            navigate("/login");
        } else if (response.status === 403) {
            addNotification("You don't have permission to send commands.", "warning");
        } else {
            console.log("Error");
        }
    }

    function keyDown(e) {
        if (e.code === "Enter") {
            var consoleInput = document.getElementById("consoleInput");
            var correctedConsoleInput = consoleInput.value;

            // if input starts with a slash, remove it
            if (correctedConsoleInput.startsWith("/")) {
                correctedConsoleInput = correctedConsoleInput.slice(1);
            }

            sendCommand(correctedConsoleInput);
            consoleInput.value = "";
        }
    }

    return (
        <div className={styles.consoleContainer}>
            <div className={styles.consoleHeader}>
                <h3>Server Console</h3>
            </div>
            <div 
                id='console'
                className={styles.console} 
                dangerouslySetInnerHTML={{ __html: serverConsole }}
            />
            <div className={styles.commandGroup}>
                <label htmlFor="consoleInput"><i className="fa-solid fa-angle-right"></i></label>
                <input id='consoleInput' name='consoleInput' className={styles.consoleInput} type="text" autoComplete="off" placeholder='Enter a command' onKeyDown={keyDown}/>
            </div>
            
        </div>
    );
}

export default Console;
