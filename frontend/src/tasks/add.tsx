import * as React from 'react';

import {useState} from 'react';
import {getConfig} from '../config';
import {createTask, getHttpClient} from '../client';
import {AxiosInstance} from 'axios';
import 'react-tabs/style/react-tabs.css';
import {Button, TextField} from "@material-ui/core";

const promiseClient: Promise<AxiosInstance> = (
    getHttpClient(getConfig())
);

export const AddTask: React.FC = () => {
    const [downloadUrl, setDownloadUrl] = useState('');

    async function handleSubmit(
        evt: React.FormEvent<HTMLFormElement>
    ): Promise<void> {
        evt.preventDefault();
        const client = await promiseClient;
        await createTask(client)({url: downloadUrl});
    }

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <p>
                    <label htmlFor="downloadUrl">URL</label>
                    <br />
                    <TextField
                        type="text"
                        id="downloadUrl"
                        name="downloadUrl"
                        value={downloadUrl}
                        onChange={e => setDownloadUrl(e.target.value)}
                        spellCheck="false"
                        autoComplete="off"
                        required
                    />
                </p>
                <p>
                    <Button variant="contained" color="primary" type="submit">
                        Download
                    </Button>
                </p>
            </form>
        </div>
    );
};