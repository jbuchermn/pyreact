import React from 'react';
import { PyreactRoot } from 'pyreact-js';


export default (_) => {
    return (
        <PyreactRoot>
            {(props) => (
                <div className="App">
                    <h1>{props.dummy ? props.dummy.counter : "Error"}</h1>
                    <div style={{backgroundColor: 'blue', width: 100, height: 100}} onClick={() => props.dummy.inc()} />
                </div>
            )}
        </PyreactRoot>
    );
}
