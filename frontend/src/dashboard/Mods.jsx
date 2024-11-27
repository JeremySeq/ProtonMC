import { useParams } from "react-router-dom";
import styles from "./Mods.module.css";
import API_SERVER from "../Constants";
import { getAuthHeader, getUserPermissionLevel } from "../AuthorizationHelper";
import { useEffect, useState } from "react";
import { useNotification } from '../NotificationContext';

function Mods() {

    const { serverName } = useParams();

    const [modList, setModList] = useState([]);

    const [searchPlatform, setSearchPlatform] = useState("curseforge");

    const [searchModList, setSearchModList] = useState([]);
    const [canInstallMods, setCanInstallMods] = useState(true);

    const { addNotification } = useNotification();

    async function downloadModsZip() {
        var prepareElement = document.getElementById("prepareModsDownload");
        prepareElement.style.visibility = "visible";
        fetch(API_SERVER + "/api/servers/" + serverName + "/mods", { headers: getAuthHeader(), method: 'GET' })
        .then(res => res.blob())
        .then(res => {
            const aElement = document.createElement('a');
            aElement.setAttribute('download', serverName + ".zip");
            const href = URL.createObjectURL(res);
            aElement.href = href;
            aElement.setAttribute('target', '_blank');
            aElement.click();
            URL.revokeObjectURL(href);
            prepareElement.style.visibility = "hidden";
        });
    }

    async function updateModList() {
        fetch(API_SERVER + "/api/servers/" + serverName + "/mods/list", { headers: getAuthHeader(), method: 'GET' })
        .then(res => res.json())
        .then(res => {
            setModList(res["data"]);
        });
    }

    async function searchMods() {
        var searchbar = document.getElementById('search-bar');
        var query = searchbar.value;

        var formData = new FormData();
        formData.append("query", query);
        formData.append("platform", searchPlatform);
        fetch(API_SERVER + "/api/servers/" + serverName + "/mods/search", { headers: getAuthHeader(), method: 'POST', body: formData})
        .then(res => res.json())
        .then(res => {
            setSearchModList(res["data"]);
        });
    }

    useEffect(() => {
        updateModList();
        searchMods();

        // check if user has permission to install mods, if not, set canInstallMods to false
        getUserPermissionLevel().then((permLevel) => {
            if (permLevel < 4) {
                setCanInstallMods(false);
            }
        })
    }, []);

    useEffect(() => {
        searchMods();
    }, [searchPlatform]);

    function switchPlatform(e) {
        if (searchPlatform == "curseforge") {
            setSearchPlatform("modrinth");
        } else {
            setSearchPlatform("curseforge");
        }
    }

    async function installMod(platform, project_id) {
        var formData = new FormData();
        formData.append("project_id", project_id);
        formData.append("platform", platform);
        fetch(API_SERVER + "/api/servers/" + serverName + "/mods/install", { headers: getAuthHeader(), method: 'POST', body: formData})
        .then(async res => {
            var data = await res.json();
            if (res.status == 200) {
                updateModList();
                addNotification("Installed mod.", "success");
            } else if (res.status == 500) {
                var err = data["error"];
                console.log(err);
                addNotification(err, "error");
            }
        });
    }

    async function deleteMod(filename) {
        var formData = new FormData();
        formData.append("filename", filename);
        fetch(API_SERVER + "/api/servers/" + serverName + "/mods/delete", { headers: getAuthHeader(), method: 'POST', body: formData})
        .then(async res => {
            var data = await res.json();
            if (res.status == 200) {
                updateModList();
                addNotification("Deleted mod.", "success");
            } else if (res.status == 500) {
                var err = data["error"];
                console.log(err);
                addNotification(err, "error");
            }
        });
    }
    
    function nFormatter(num, digits) {
        const lookup = [
          { value: 1, symbol: "" },
          { value: 1e3, symbol: "k" },
          { value: 1e6, symbol: "M" },
          { value: 1e9, symbol: "G" },
          { value: 1e12, symbol: "T" },
          { value: 1e15, symbol: "P" },
          { value: 1e18, symbol: "E" }
        ];
        const regexp = /\.0+$|(?<=\.[0-9]*[1-9])0+$/;
        const item = lookup.findLast(item => num >= item.value);
        return item ? (num / item.value).toFixed(digits).replace(regexp, "").concat(item.symbol) : "0";
      }

    return (
        <div className={styles.modsContainer}>
            <div className={styles.modManagerContainer}>
                <div className={styles.column}>
                    <h2>{modList.length} mods installed</h2>
                    <ul className={styles.modList}>
                        {modList.map((modListItem) => (
                            <li key={modListItem[0]} className={styles.modListItem}>
                                <p>{modListItem[1]}</p>
                                <button onClick={() => deleteMod(modListItem[0])}><i className="fa-solid fa-trash"></i></button>
                            </li>
                        ))}
                    </ul>
                    <button className={styles.downloadModsButton} onClick={downloadModsZip}>Download Mods</button>
                    <div style={{visibility: "hidden"}} id="prepareModsDownload" className={styles.prepareDownload}>
                        Preparing download. Please wait...
                    </div>
                </div>

                { // check if the user can install mods, if they can, then show the search mods stuff, if not then don't show anything
                    canInstallMods ? 

                <div className={styles.modSearchContainer}>
                    <h2>Search Mods on <i onClick={switchPlatform} className={searchPlatform == "curseforge" ? styles.curseforgePlatform : styles.modrinthPlatform}></i></h2>
                    <div className={styles.searchContainer}>
                        <input type="text" className={styles.searchBar} onChange={searchMods} id="search-bar" placeholder="Search mods..."></input>
                        <button className={styles.searchButton} id="search-button"><i className="fa-solid fa-magnifying-glass"></i></button>
                    </div>

                    <div className={styles.resultsContainer}>

                        {searchModList.map((item) => (

                            <div className={styles.resultItem}>
                                <img src={item["logo"]} alt="" style={{"borderRadius": item["platform"] == 2 ? "15px" : "0px"}} />
                                <div>
                                    <h3><a href={item["link"]} target="_blank">{item["name"]}</a><i> by {item["author"]}</i></h3>
                                    <p>{nFormatter(item["downloads"], 1)} Downloads</p>
                                </div>
                                <button onClick={() => installMod(item["platform"], item["project_id"])} className={styles.installButton}>Install</button>
                            </div>
                        ))}
                    </div>
                </div>
                : ""}
            </div>
        </div>
    )
}

export default Mods;