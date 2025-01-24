import React, { useState, useEffect } from 'react';
import axios from 'axios';

function FileList() {
    const [files, setFiles] = useState([]);

    useEffect(() => {
        const fetchFiles = async () => {
            const token = localStorage.getItem('token');
            try {
                const response = await axios.get('http://localhost:8000/files/', {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                setFiles(response.data);
            } catch (error) {
                console.error(error);
                alert('Failed to fetch files');
            }
        };

        fetchFiles();
    }, []);

    const handleDownload = async (fileId, filename) => {
        const token = localStorage.getItem('token');
        try {
            const response = await axios.get(`http://localhost:8000/download/${fileId}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
                responseType: 'blob',
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
        } catch (error) {
            console.error(error);
            alert('Failed to download file');
        }
    };

    return (
        <div>
            <h2>Files</h2>
            <ul>
                {files.map((file) => (
                    <li key={file.id}>
                        {file.filename}
                        <button onClick={() => handleDownload(file.id, file.filename)}>Download</button>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default FileList;
