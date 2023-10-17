import React, { useState, useEffect } from "react";
import ApplicationPage from "./application";
import LoginPage from "./login/LoginPage";
import $ from "jquery";
import boardsSlice from "./redux/boardsSlice";
import { useDispatch, useSelector } from "react-redux";

function App() {
  const [auth, setAuth] = useState(false);
  const boardData = useSelector((state) => state.boards);
  const dispatch = useDispatch();

  const getDataFunction = () => {
    $.ajax({
      url: "http://localhost:5000/getBoards",
      method: "POST",
      headers: {
        Authorization: "Bearer " + localStorage.getItem("token"),
        "Access-Control-Allow-Origin": "http://localhost:3000",
        "Access-Control-Allow-Credentials": "true",
      },
      credentials: "include",
      data: JSON.stringify({
        test: "test",
      }),
      success: (boards) => {
        dispatch(boardsSlice.actions.setInitialData({ initialData: boards }));
        console.log("SRJ BOARDS", boards);
        console.log("boards", boardData);
      },
    });
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    dispatch(boardsSlice.actions.deleteInitialData());
    setCurrentPage(
      <LoginPage
        side={() =>
          setCurrentPage(
            <ApplicationPage
              initialData={boardData}
              getData={getDataFunction}
              logout={handleLogout}
            />
          )
        }
      />
    );
    setAuth(false);
  };

  const [currentPage, setCurrentPage] = useState(
    <LoginPage
      side={() =>
        setCurrentPage(
          <ApplicationPage
            initialData={boardData}
            getData={getDataFunction}
            logout={handleLogout}
          />
        )
      }
    />
  );

  useEffect(() => {
    if (localStorage.getItem("token")) {
      setAuth(true);
      setCurrentPage(
        <ApplicationPage
          initialData={boardData}
          getData={getDataFunction}
          logout={handleLogout}
        />
      );
    }
  }, [auth]);

  return <div className="main-page">{currentPage}</div>;
}

export default App;
