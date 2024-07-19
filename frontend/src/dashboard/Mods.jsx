import { useParams } from "react-router-dom";
import styles from "./Mods.module.css";
import API_SERVER from "../Constants";
import { getAuthHeader } from "../AuthorizationHelper";

function Mods() {

    const { serverName } = useParams();

    async function downloadMods() {
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

    return (
        <div className={styles.modsContainer}>
            <h2>Mods</h2>
            <button className={styles.downloadModsButton} onClick={downloadMods}>Download Mods</button>
            <div style={{visibility: "hidden"}} id="prepareModsDownload" className={styles.prepareDownload}>
                Preparing download. Please wait...
            </div>
        </div>
    )
}

export default Mods;