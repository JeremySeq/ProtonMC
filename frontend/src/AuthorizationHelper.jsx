import API_SERVER from './Constants.jsx'

function getCookie(cname) {
    let name = cname + "=";
    let decodedCookie = decodeURIComponent(document.cookie);
    let ca = decodedCookie.split(';');
    for(let i = 0; i <ca.length; i++) {
      let c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
}

export function setAuthCookie(token) {
  document.cookie = `Authorization=${encodeURIComponent(token)}; path=/`;
}

export function getAuthHeader() {
    var token = getCookie("Authorization");
    return {
        "Authorization": "Bearer " + token
    }
}

export function hasAuth() {
  var token = getCookie("Authorization");
  
  if (token) {
    return true;
  }
  return false;
}

export async function isAuthenticated() {
  var token = getCookie("Authorization");
  
  if (token) {
    const response = await fetch(API_SERVER + "/api/login/validate", {
        headers: getAuthHeader()
    });
    if (response.status == 200) {
        return true;
    } else if (response.status == 401) {
        return false;
    } else {
      console.log("Error code: " + response.status)
      return false;
    }
  }
  return false;
}

export async function getUserPermissionLevel() {
  var token = getCookie("Authorization");
  
  if (token) {
    const response = await fetch(API_SERVER + "/api/login/", {
        method: "GET",
        headers: getAuthHeader()
    });
    const userInfo = await response.json();
    if (response.status == 200) {
        return userInfo["permissions"];
    } else if (response.status == 401) {
        return false;
    } else {
      console.log("Error code: " + response.status)
      return false;
    }
  }
}