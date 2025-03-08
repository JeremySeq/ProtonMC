import { useState } from 'react';
import styles from './LoginPage.module.css'
import API_SERVER from './Constants';
import { useNavigate } from 'react-router-dom';
import { setAuthCookie } from './AuthorizationHelper';

function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const navigate = useNavigate();
  
    const handleEmailChange = (e) => {
      setUsername(e.target.value);
    };
  
    const handlePasswordChange = (e) => {
      setPassword(e.target.value);
    };

    const login = async () => {
      var formData = new FormData();
      formData.append("username", username);
      formData.append("password", password);

      const response = await fetch(API_SERVER + "/api/login/", {
          method: "POST",
          body: formData
      });
      const data = await response.json();
      if (response.status == 200) {
        console.log(data["message"]);
        setAuthCookie(data["token"], username);
        navigate("/servers");
      } else {
        alert(data["message"]);
        console.log(data["message"]);
      }
    };

    const togglePasswordVisibility = (e) => {
      var x = document.getElementById("password");
      if (x.type === "password") {
        x.type = "text";
      } else {
        x.type = "password";
      }
    }
  
    const handleSubmit = (e) => {
      e.preventDefault();
      login();
    };
  
    return (
        <>
            <h1 className={styles.header}></h1>
            <div className={styles.container}>
                <form onSubmit={handleSubmit} className={styles.form}>
                    <img className={styles.logo} src="/assets/logo.svg" alt="logo"/>
                    <h2>Login</h2>
                    <div className={styles.inputGroup}>
                        <label htmlFor="username">Username:</label>
                        <input
                            type="username"
                            id="username"
                            value={username}
                            onChange={handleEmailChange}
                            required
                            className={styles.input}
                            placeholder='Username'
                        />
                    </div>
                    <div className={styles.inputGroup}>
                        <label htmlFor="password">Password:</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={handlePasswordChange}
                            required
                            className={styles.input}
                            placeholder='Password'
                        />
                    </div>

                    <button type="submit" className={styles.button}>Login<i
                        className="fa-solid fa-right-to-bracket"></i></button>
                </form>
            </div>
        </>
    );
}

export default LoginPage
