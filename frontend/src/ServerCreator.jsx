import {useEffect, useState} from "react";
import styles from './ServerCreator.module.css';
import API_SERVER from "./Constants.jsx";
import {getAuthHeader} from "./AuthorizationHelper.jsx";
import {useNavigate} from "react-router-dom";

function ServerCreator() {

    const [minecraftVersions, setMinecraftVersions] = useState([]);
    const [selectedServerType, setSelectedServerType] = useState("spigot");
    const [selectedMinecraftVersion, setSelectedMinecraftVersion] = useState("");
    const [serverName, setServerName] = useState("");
    const navigate = useNavigate();

    function updateSelectedServerType(event) {
        setSelectedServerType(event.target.value);
    }

    function updateSelectedMinecraftVersion(event) {
        setSelectedMinecraftVersion(event.target.value);
    }

    useEffect(() => {

        async function fetchVersions() {
            const response = await fetch(API_SERVER + "/api/servers/game_versions?type=" + selectedServerType, {
                headers: getAuthHeader()
            });
            const versionList = await response.json();
            if (response.status == 200) {
                setMinecraftVersions(versionList["message"])
                setSelectedMinecraftVersion(versionList["message"][0]);
            } else if (response.status == 401) {
                navigate("/login");
                // alert("You are not logged in.")
            } else {
                console.log("Error")
            }
        }

        fetchVersions();
    }, [selectedServerType]);

    async function createMinecraftServer() {
        console.log(serverName, selectedServerType, selectedMinecraftVersion);

        var form = new FormData();
        form.set("name", serverName);
        form.set("type", selectedServerType);
        form.set("version", selectedMinecraftVersion);

        const response = await fetch(API_SERVER + "/api/servers/", {
            headers: getAuthHeader(),
            method: "POST",
            body: form
        });
        const json = await response.json();
        if (response.status == 200) {
            navigate("/servers")
        } else if (response.status == 401) {
            navigate("/login");
            alert("You are not logged in.")
        } else {
            console.log("Error: " + json["message"])
        }
    }

    function updateServerName(event) {
        setServerName(event.target.value);
        console.log(event.target.value);
    }

    return (
        <>

            <div className={styles.container}>
                <button onClick={() => navigate("/servers")} className={styles.backBtn}><i className="fa-solid fa-arrow-left"></i></button>
                <h1>Create Server</h1>

                <label>Server Name</label>
                <input value={serverName} onChange={updateServerName} placeholder="Name" id="server-name" type="text"/>

                <label>Server Type</label>
                <select onChange={updateSelectedServerType} value={selectedServerType} name="server-types"
                        id="server-types">
                    <option value="spigot">Spigot</option>
                    <option value="forge">Forge</option>
                    <option value="neoforge">NeoForge</option>
                    <option value="fabric">Fabric</option>
                </select>

                <label>Minecraft Version</label>
                <select onChange={updateSelectedMinecraftVersion} value={selectedMinecraftVersion}
                        name="minecraft-versions" id="minecraft-versions">
                    {minecraftVersions.map((minecraftVersion) => (
                        <option key={minecraftVersion} value={minecraftVersion}>{minecraftVersion}</option>
                    ))}
                </select>

                <button onClick={createMinecraftServer}>Create Server</button>
            </div>

        </>
    )
}

export default ServerCreator;