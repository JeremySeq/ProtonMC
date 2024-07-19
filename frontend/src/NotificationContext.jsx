import { createContext, useState, useContext } from 'react';
import Notification from './Notification';

const NotificationContext = createContext();

export const useNotification = () => {
    return useContext(NotificationContext);
};

export const NotificationProvider = ({ children }) => {
    NotificationProvider.propTypes = {
        children
    }
    const [notifications, setNotifications] = useState([]);

    const addNotification = (message, type) => {
        const id = new Date().getTime();
        const newNotification = { id, message, type };
        setNotifications(prevNotifications => [...prevNotifications, newNotification]);
    };

    const removeNotification = (idToRemove) => {
        setNotifications(prevNotifications =>
            prevNotifications.filter(notification => notification.id !== idToRemove)
        );
    };

    return (
        <NotificationContext.Provider value={{ addNotification }}>
            {children}
            <div className="notification-container">
                {notifications.map(notification => (
                    <Notification
                        key={notification.id}
                        notification={notification}
                        message={notification.message}
                        type={notification.type}
                        onClose={() => removeNotification(notification.id)}
                    />
                ))}
            </div>
        </NotificationContext.Provider>
    );
};
