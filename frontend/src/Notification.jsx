import { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';


const Notification = ({ id, message, type, onClose }) => {
    const touchStartX = useRef(0);
    const touchCurrentX = useRef(0);
    const [translateX, setTranslateX] = useState(0);

    useEffect(() => {
        const timer = setTimeout(() => {
            onClose();
        }, 3000);
        return () => clearTimeout(timer);
    }, [onClose]);

    const handleTouchStart = (e) => {
        touchStartX.current = e.targetTouches[0].clientX;
        touchCurrentX.current = touchStartX.current;
    };

    const handleTouchMove = (e) => {
        touchCurrentX.current = e.targetTouches[0].clientX;
        setTranslateX((touchCurrentX.current - touchStartX.current));
    };

    const handleTouchEnd = () => {
        if (touchCurrentX.current - touchStartX.current > 50) {
            // Swipe right, then close the notification
            setTranslateX(500)
            setTimeout(() => {
                onClose();
            }, 300); // Match the duration of the slide-out transition
        } else {
            // Reset position if swipe is not sufficient
            setTranslateX(0);
        }
    };

    const getIcon = () => {
        if (type == "success") {
            return <i className="fa-solid fa-circle-check"></i>;
        } else if (type == "error") {
            return <i className="fa-solid fa-circle-exclamation"></i>;
        } else if (type == "warning") {
            return <i className="fa-solid fa-triangle-exclamation"></i>;
        }
    }

    return (
        <div
            id={`notification-${id}`}
            className={`notification ${type}`}
            onTouchStart={handleTouchStart}
            onTouchMove={handleTouchMove}
            onTouchEnd={handleTouchEnd}
            style={{ transform: `translateX(${translateX}px)` }}
        >{getIcon()}
            {message}
            <button className="close-btn" onClick={onClose}>
                <i className="fa-solid fa-xmark"></i>
            </button>
        </div>
    );
};

Notification.propTypes = {
    id: PropTypes.number,
    message: PropTypes.string,
    type: PropTypes.string,
    onClose: PropTypes.func
}


export default Notification;
