import React, { useState } from "react";
import "./LoginPage.css"; // Import the local CSS file
import $ from "jquery";

import { getToken, signUp, storeToken } from "../api/loginHandler";

const LoginPage = ({ side }) => {
  const [activeTab, setActiveTab] = useState("login");
  const [loginData, setLoginData] = useState({ username: "", password: "" });
  const [signupData, setSignupData] = useState({
    fullName: "",
    username: "",
    password: "",
  });

  const handleTabChange = (tabKey) => {
    setActiveTab(tabKey);
  };

  const handleLogin = () => {
    console.log("Login click");
    getToken(loginData)
      .then((res) => {
        console.log("SRj", JSON.stringify(res));
        if (res["error"]) throw new Error("Wrong username or password");
        storeToken(res);
        side();
      })
      .catch((error) => {
        console.log(error);
        alert("Error while login ! Wrong username or password");
      });
  };

  const handleSignup = () => {
    console.log("Signup click");
    //console.log(obj)
    signUp(signupData)
      .then((res) => {
        alert("Sign up successfull! Proceed to Login");
      })
      .catch((error) => {
        alert("Error while signing up !");
      });
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-inner">
        <ul className="nav nav-tabs">
          <li className={`nav-item ${activeTab === "login" ? "active" : ""}`}>
            <button
              className="nav-link"
              onClick={() => handleTabChange("login")}
            >
              Login
            </button>
          </li>
          <li className={`nav-item ${activeTab === "signup" ? "active" : ""}`}>
            <button
              className="nav-link"
              onClick={() => handleTabChange("signup")}
            >
              Signup
            </button>
          </li>
        </ul>

        {activeTab === "login" && (
          <form>
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                className="form-control"
                placeholder="Enter username"
                value={loginData.username}
                onChange={(e) =>
                  setLoginData({ ...loginData, username: e.target.value })
                }
              />
            </div>

            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                className="form-control"
                placeholder="Enter password"
                value={loginData.password}
                onChange={(e) =>
                  setLoginData({ ...loginData, password: e.target.value })
                }
              />
            </div>

            <button
              type="button"
              onClick={handleLogin}
              className="btn btn-secondary btn-block"
            >
              Login
            </button>
          </form>
        )}

        {activeTab === "signup" && (
          <form>
            <div className="form-group">
              <label>Full name</label>
              <input
                type="text"
                className="form-control"
                placeholder="Full name"
                value={signupData.fullName}
                onChange={(e) =>
                  setSignupData({ ...signupData, fullName: e.target.value })
                }
              />
            </div>

            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                className="form-control"
                placeholder="Enter username"
                value={signupData.username}
                onChange={(e) =>
                  setSignupData({ ...signupData, username: e.target.value })
                }
              />
            </div>

            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                className="form-control"
                placeholder="Enter password"
                value={signupData.password}
                onChange={(e) =>
                  setSignupData({ ...signupData, password: e.target.value })
                }
              />
            </div>

            <button
              type="button"
              onClick={handleSignup}
              className="btn btn-secondary btn-block"
            >
              Sign Up
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default LoginPage;
