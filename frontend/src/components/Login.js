import React, { useState } from "react";
import { Tabs, Tab } from "react-bootstrap";
import { getToken, signUp, storeToken } from "../api/loginHandler";

const LoginPage = (props) => {
  const [loginData, setLoginData] = useState({
    username: "",
    password: "",
  });

  const [signupData, setSignupData] = useState({
    fullname: "",
    username: "",
    password: "",
  });

  const handleLogin = () => {
    const { username, password } = loginData;
    console.log("Login click");
    const obj = {
      username,
      password,
    };

    getToken(obj)
      .then((res) => {
        console.log(res);
        if (res.error) throw new Error("Wrong username or password");
        storeToken(res);
        props.side();
      })
      .catch((error) => {
        console.log(error);
        alert("Error while login! Wrong username or password");
      });
  };

  const handleSignup = () => {
    const { fullname, username, password } = signupData;
    console.log("Signup click");
    const obj = {
      username,
      password,
      fullName: fullname,
    };

    signUp(obj)
      .then(() => {
        alert("Sign up successful! Proceed to Login");
      })
      .catch(() => {
        alert("Error while signing up!");
      });
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-inner">
        <Tabs
          defaultActiveKey="login"
          id="logintab"
          className="mx-auto"
          style={{ paddingLeft: "25%" }}
        >
          <Tab eventKey="login" title="Login">
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
          </Tab>
          <Tab eventKey="signup" title="Signup">
            <form>
              <div className="form-group">
                <label>Full name</label>
                <input
                  type="text"
                  className="form-control"
                  placeholder="Full name"
                  value={signupData.fullname}
                  onChange={(e) =>
                    setSignupData({ ...signupData, fullname: e.target.value })
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
          </Tab>
        </Tabs>
      </div>
    </div>
  );
};

export default LoginPage;
