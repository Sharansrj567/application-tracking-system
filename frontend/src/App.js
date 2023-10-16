import React, { useState, useEffect } from "react";
import ApplicationPage from "./application";
import LoginPage from "./login/LoginPage";

function App() {
  const [auth, setAuth] = useState(false);
  const handleLogout = () => {
    localStorage.removeItem("token");
    setCurrentPage(
      <LoginPage
        side={() => setCurrentPage(<ApplicationPage logout={handleLogout} />)}
      />
    );
    setAuth(false);
  };
  const [currentPage, setCurrentPage] = useState(
    <LoginPage
      side={() => setCurrentPage(<ApplicationPage logout={handleLogout} />)}
    />
  );

  useEffect(() => {
    if (localStorage.getItem("token")) {
      setAuth(true);
      setCurrentPage(<ApplicationPage logout={handleLogout} />);
    }
  }, [auth]);

  return <div className="main-page">{currentPage}</div>;
}

export default App;