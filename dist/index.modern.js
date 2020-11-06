import React from 'react';

function _inheritsLoose(subClass, superClass) {
  subClass.prototype = Object.create(superClass.prototype);
  subClass.prototype.constructor = subClass;
  subClass.__proto__ = superClass;
}

var connect = function connect(port, onMessage, initialMsg) {
  var socket = new WebSocket("ws://" + location.hostname + ":" + port);

  socket.onopen = function (_) {
    console.log("[ws:open] Connection established");
    socket.send(JSON.stringify(initialMsg));
  };

  socket.onmessage = function (event) {
    console.log("[ws:message] Data received from server: " + event.data);
    onMessage(JSON.parse(event.data), function (msg) {
      return socket.send(JSON.stringify(msg));
    });
  };

  socket.onclose = function (_) {
    console.log('[ws:close] Connection closed... reconnecting...');
    setTimeout(function () {
      return connect(port, onMessage, initialMsg);
    }, 200);
  };

  socket.onerror = function (error) {
    console.log("[ws:error] " + error.message);
  };
};

var unwrap = function unwrap(props, send) {
  if (props === undefined || props === null) {
    return props;
  } else if (Array.isArray(props)) {
    return props.map(function (p) {
      return unwrap(p);
    });
  } else if (typeof props === "object") {
    var res = {};
    Object.keys(props).forEach(function (k) {
      return res[k] = unwrap(props[k], send);
    });
    return res;
  } else {
    if (typeof props === "string" && props.includes("__pyreact_pyfunc")) {
      return function () {
        for (var _len = arguments.length, args = new Array(_len), _key = 0; _key < _len; _key++) {
          args[_key] = arguments[_key];
        }

        return send({
          '__pyreact_kind': 'func_call',
          '__pyreact_id': props,
          '__pyreact_args': args
        });
      };
    }

    return props;
  }
};

var PyreactRoot = /*#__PURE__*/function (_React$Component) {
  _inheritsLoose(PyreactRoot, _React$Component);

  function PyreactRoot(props) {
    var _this;

    _this = _React$Component.call(this, props) || this;
    _this.state = {
      props: {}
    };
    return _this;
  }

  var _proto = PyreactRoot.prototype;

  _proto.componentDidMount = function componentDidMount() {
    var _this2 = this;

    connect(this.props.port || 8081, function (msg, send) {
      var props = unwrap(msg.props, send);
      console.log("[pyreact-root]", props);

      _this2.setState({
        props: props
      });
    }, {
      '__pyreact_kind': 'request_render'
    });
  };

  _proto.render = function render() {
    return this.props.children(this.state.props);
  };

  return PyreactRoot;
}(React.Component);

export { PyreactRoot };
//# sourceMappingURL=index.modern.js.map
