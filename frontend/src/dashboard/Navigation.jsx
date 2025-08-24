import { Link, useLocation } from 'react-router-dom';
import styles from "./Navigation.module.css";
import PropTypes from 'prop-types';
import isMobile from "./useIsMobile.js";

export default function Navigation({ sidebarLinks, sidebarOpen }) {
    const location = useLocation();
    const currentPath = location.pathname;

    // not mobile = sidebar
    if (!isMobile()) {
        return (
            <div
                className={`${styles.sidebar} ${sidebarOpen ? styles.sidebarOpen : ""}`}
                id="sidebar"
            >
                <div className={styles.links}>
                    {sidebarLinks.map((link) => (
                        <Link
                            key={link.path}
                            to={link.path}
                            className={currentPath === link.path ? styles.activeLink : ""}
                        >
                            <i className={link.icon}></i>
                            {link.label}
                        </Link>
                    ))}
                </div>
            </div>
        );
    }

    // mobile = bottom navbar
    return (
        <div className={styles.bottomNav}>
            {sidebarLinks.map((link) => (
                <Link
                    key={link.path}
                    to={link.path}
                    className={`${styles.navBtn} ${currentPath === link.path ? styles.selected : ""}`}
                >
                    <i className={link.icon}></i>
                </Link>
            ))}
        </div>
    );
}

Navigation.propTypes = {
    sidebarLinks: PropTypes.arrayOf(
        PropTypes.shape({
            path: PropTypes.string.isRequired,
            icon: PropTypes.string.isRequired,
            label: PropTypes.string.isRequired,
        })
    ).isRequired,
    sidebarOpen: PropTypes.booleanValue
};
