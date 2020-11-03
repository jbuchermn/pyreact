import React from 'react'

const connect = (onMessage, initialMsg) => {
    let socket = new WebSocket("ws://localhost:8081");

    socket.onopen = (_) => {
        console.log("[ws:open] Connection established");
        socket.send(JSON.stringify(initialMsg));
    };

    socket.onmessage = (event) => {
        console.log(`[ws:message] Data received from server: ${event.data}`);
        onMessage(JSON.parse(event.data), (msg) => socket.send(JSON.stringify(msg)));
    };

    socket.onclose = (_) => {
        console.log('[ws:close] Connection closed... reconnecting...');
        setTimeout(() => connect(onMessage, initialMsg), 200);
    };

    socket.onerror = (error) => {
        console.log(`[ws:error] ${error.message}`);
    };
}

const unwrap = (props, send) => {
    if (props === undefined || props === null){
        return props;
    }else if (Array.isArray(props)) {
        return props.map(p => unwrap(p));
    } else if (typeof props === "object") {
        let res = {};
        Object.keys(props).forEach(k => res[k] = unwrap(props[k], send));
        return res;
    } else {
        if (typeof props === "string" && props.includes("__pyreact_pyfunc")) {
            return ((...args) => send({
                '__pyreact_kind': 'func_call',
                '__pyreact_id': props,
                '__pyreact_args': args,
            }));
        }
        return props;
    }
}

export default class PyreactRoot extends React.Component {
    constructor(props) {
        super(props);
        this.state = { props: {} };
    }

    componentDidMount(){
        connect((msg, send) => {
            let props = unwrap(msg.props, send);
            console.log("[pyreact-root]", props)
            this.setState({props});

        }, {'__pyreact_kind': 'request_render'});
    }

    render() {
        return this.props.children(this.state.props);
    }
}
