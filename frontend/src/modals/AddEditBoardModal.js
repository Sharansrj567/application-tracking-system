import React, { useState } from "react";
import crossIcon from "../assets/icon-cross.svg";
import boardsSlice from "../redux/boardsSlice";
import { v4 as uuidv4 } from "uuid";
import { useDispatch, useSelector } from "react-redux";
import $ from 'jquery';

function AddEditBoardModal({ setIsBoardModalOpen, type }) {
  const dispatch = useDispatch();
  const [isFirstLoad, setIsFirstLoad] = useState(true);
  const [boardName, setBoardName] = useState("");
  const [newColumns, setNewColumns] = useState([
    { name: "Applied", tasks: [], id: uuidv4() },
    { name: "Rejected", tasks: [], id: uuidv4() },
    { name: "Waiting For Referral", tasks: [], id: uuidv4() },
  ]);
  const [isValid, setIsValid] = useState(true);
  const board = useSelector((state) => state.boards).find(
    (board) => board.isActive
  );

  if (type === "edit" && isFirstLoad) {
    setNewColumns(
      board.columns.map((col) => {
        return { ...col, id: uuidv4() };
      })
    );
    setBoardName(board.name);
    setIsFirstLoad(false);
  }

  const validate = () => {
    setIsValid(false);
    if (!boardName.trim()) {
      return false;
    }
    for (let i = 0; i < newColumns.length; i++) {
      if (!newColumns[i].name.trim()) {
        return false;
      }
    }
    setIsValid(true);
    return true;
  };

  const onChangeColumnName = (id, newValue) => {
    setNewColumns((prevState) => {
      const newState = [...prevState];
      const column = newState.find((col) => col.id === id);
      column.name = newValue;
      return newState;
    });
  };

  const onDeleteColumn = (id) => {
    setNewColumns((prevState) => prevState.filter((el) => el.id !== id));
  };

  // const createNewBoard = (application) => {
  //   const newApplications = this.state.applications 
  //   if (application.id == null) {
  //     // current board is a new board, create a new one and save in the backend.
  //     $.ajax({
  //       url: 'http://localhost:5000/boards', // TODO: will have to replace with production URL
  //       method: 'POST',
  //       headers: {
  //         Authorization: 'Bearer ' + localStorage.getItem('token'),
  //         'Access-Control-Allow-Origin': 'http://localhost:3000',
  //         'Access-Control-Allow-Credentials': 'true'
  //       },
  //       async: false,
  //       data: JSON.stringify({
  //         application: application
  //       }),
  //       contentType: 'application/json',
  //       success: (msg) => {
  //         console.log(msg)
  //       },
  //       complete: function (data) {
  //         newApplications.push(data.responseJSON)
  //       }
  //     })
  //   } else {
  //     console.log('updating id=' + application.id)
  //     // $.ajax({
  //     //   url: 'http://localhost:5000/board/' + application.id,
  //     //   method: 'PUT',
  //     //   async: false,
  //     //   data: JSON.stringify({
  //     //     application: application
  //     //   }),
  //     //   headers: {
  //     //     Authorization: 'Bearer ' + localStorage.getItem('token'),
  //     //     'Access-Control-Allow-Origin': 'http://localhost:3000',
  //     //     'Access-Control-Allow-Credentials': 'true'
  //     //   },
  //     //   contentType: 'application/json',
  //     //   success: (msg) => {
  //     //     console.log(msg)
  //     //   },
  //     //   complete: function (data) {
  //     //     const updatedApp = data.responseJSON
  //     //     const idx = newApplications.findIndex(a => a.id === updatedApp.id)
  //     //     newApplications[idx] = updatedApp
  //     //   }
  //     // })
  //   }
  //   this.renderPage(newApplications)
  // }
  const createNewBoard = () => {

    // const newApplications = board // initialize array
  
      // Create new board
      $.ajax({
        url: 'http://localhost:5000/boards',  
        method: 'POST',
        data: {boardName:boardName},
        success: (boardName) => {
          console.log("yessS")
          // newApplications.push(board);
        }
      });
    // Render UI with updated boards
    // this.renderPage(newApplications);
  
  }

  const deleteBoard = () => {

    // const newApplications = board // initialize array
  
      // Create new board
      $.ajax({
        url: 'http://localhost:5000/boards',  
        method: 'DELETE',
        data: {boardName:boardName},
        success: (boardName) => {
          console.log("yessS")
          // newApplications.push(board);
        }
      });
    // Render UI with updated boards
    // this.renderPage(newApplications);
  }

  const editBoard = () => {

    // const newApplications = board // initialize array
  
      // Create new board
      $.ajax({
        url: 'http://localhost:5000/boards',  
        method: 'PUT',
        data: {boardName:boardName},
        success: (boardName) => {
          console.log("yessS")
          // newApplications.push(board);
        }
      });
    // Render UI with updated boards
    // this.renderPage(newApplications);
  }

  const onSubmit = (type) => {
    setIsBoardModalOpen(false);
    if (type === "add") {
      dispatch(boardsSlice.actions.addBoard({ name: boardName, newColumns }));
    } else {
      dispatch(boardsSlice.actions.editBoard({ name: boardName, newColumns }));
    }
  };

  return (
    <div
      className="fixed right-0 top-0 px-2 py-4 overflow-scroll scrollbar-hide z-50 left-0 bottom-0 justify-center items-center flex dropdown"
      onClick={(e) => {
        if (e.target !== e.currentTarget) {
          return;
        }
        setIsBoardModalOpen(false);
      }}
    >
      <div
        className="scrollbar-hide overflow-y-scroll max-h-[95vh] bg-white dark:bg-[#2b2c37] text-black dark:text-white font-bold
       shadow-md shadow-[#364e7e1a] max-w-md mx-auto my-auto w-full px-8 py-8 rounded-xl"
      >
        <h3 className="text-lg">
          {type === "edit" ? "Edit" : "Add New"} Board
        </h3>

        <div className="mt-8 flex flex-col space-y-1">
          <label className="text-sm dark:text-white text-gray-500">
            Board Name
          </label>
          <input
            className="bg-transparent px-4 py-2 rounded-md text-sm border-[0.5px] border-gray-600 focus:outline-[#635fc7] outline-1 ring-0"
            placeholder="e.g Web Design"
            value={boardName}
            onChange={(e) => setBoardName(e.target.value)}
            id="board-name-input"
          />
        </div>

        <div className="mt-8 flex flex-col space-y-3">
          <label className="text-sm dark:text-white text-gray-500">
            Board Columns
          </label>

          {newColumns.map((column, index) => (
            <div key={index} className="flex items-center w-full">
              <input
                className="bg-transparent flex-grow px-4 py-2 rounded-md text-sm border-[0.5px] border-gray-600 focus:outline-[#635fc7] outline-[1px]"
                onChange={(e) => {
                  onChangeColumnName(column.id, e.target.value);
                  editBoard(boardName)
                }}
                type="text"
                value={column.name}
              />
              <img
                src={crossIcon}
                onClick={() => {
                  onDeleteColumn(column.id);
                  deleteBoard(boardName)
                }}
                className="m-4 cursor-pointer"
              />
            </div>
          ))}
          <div>
            <button
              className="w-full items-center hover:opacity-70 dark:text-[#635fc7] dark:bg-white text-white bg-[#635fc7] py-2 rounded-full"
              onClick={() => {
                setNewColumns((state) => [
                  ...state,
                  { name: "", tasks: [], id: uuidv4() },
                ]);
              }}
            >
              + Add New Column
            </button>
            <button
              onClick={() => {
                const isValid = validate();
                if (isValid === true) onSubmit(type);
                createNewBoard(boardName)
              }}
              className="w-full items-center hover:opacity-70 dark:text-white dark:bg-[#635fc7] mt-8 relative text-white bg-[#635fc7] py-2 rounded-full"
            >
              {type === "add" ? "Create New Board" : "Save Changes"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AddEditBoardModal;
