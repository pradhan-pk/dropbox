import React from 'react';
import Register from './components/Register';
import Login from './components/Login';
import UploadFile from './components/UploadFile';
import FileList from './components/FileList';

function App() {
    return (
        <div>
            <h1>Dropbox Clone</h1>
            <Register />
            <Login />
            <UploadFile />
            <FileList />
        </div>
    );
}

export default App;
