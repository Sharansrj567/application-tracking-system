import React, { useState, useEffect } from "react";
import ApplicationPage from "./application";
import LoginPage from "./login/LoginPage";

function App() {
  const [currentPage, setCurrentPage] = useState(<LoginPage />);
  const [auth, setAuth] = useState(false);
  const handleLogout = () => {
    localStorage.removeItem("token");
    setCurrentPage(mapRouter["LoginPage"]);
    setAuth(false);
  };

  const mapRouter = {
    ApplicationPage: <ApplicationPage logout={handleLogout} />,
    LoginPage: (
      <LoginPage side={() => setCurrentPage(mapRouter["ApplicationPage"])} />
    ),
  };

  useEffect(() => {
    if (localStorage.getItem("token")) {
      setAuth(true);
      setCurrentPage(mapRouter["ApplicationPage"]);
    }
  }, [auth]);

  return <div className="main-page">{currentPage}</div>;
}

export default App;
