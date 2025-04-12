Ext.ns('core');

var seq = 0;

var _RemoteObserver = function() {
    this.tryReconnectCount = 0;
    this.connected = false;
    this.events = {};
    this.init();
}

_RemoteObserver.prototype = {
    init: function(reset) {
        reset = (reset || true);

        if (localStorage.getItem('disableWebsocket') === 'on') {
            console.warn('Websocket desabilitado por configuração.');
        } else if (!this.connected) {
            this.tryReconnectCount = (reset ? 0 : this.tryReconnectCount);
            this._init();
        } else {
            console.log('core.RemoteObserver já esta conectado.');
        }
    },

    _init: function() {
        var url = [
            (location.protocol === 'https:' ? 'wss' : 'ws'),
            '://',
            location.host,
            '/ws'
        ].join('');
        var self = this;
        var ws = new WebSocket(url);

        ws.onerror = function() {
            console.warn('core.RemoteObserver não pode ser iniciado.');
            self.connected = false;
        };

        ws.onopen = function() {
            console.info('core.RemoteObserver conectado com sucesso.');
            self.connected = true;
        };

        ws.onclose = function() {
            console.info('core.RemoteObserver foi desconectado.');
            self.connected = false;
            ws.close();

            self.tryReconnectCount = (self.tryReconnectCount || 0) + 1;
            if (self.tryReconnectCount < 5) {
                setTimeout(function() { self.init(false); }, 1000);
            } else {
                setTimeout(
                    function() {
                        self.tryReconnectCount = 0;
                        self.init();
                    },
                    (30 * 1000)
                );
            }
        };

        ws.onmessage = function(message) {
            try {
                self._routeMessage(JSON.parse(message.data));
            } catch (e) {
                console.error(e);
            }
        };
    },

    _routeMessage: function(message) {
        this.emmit(message.event, message.options);
    },

    emmit: function(name, options) {
        (this.events[name] || [])
            .forEach(function(cb) {
                setTimeout(function() {
                    core.invokeCallback(cb || { fn: Ext.emptyFn }, options)
                },
                1
            );
        });
    },

    un: function(name, cb) {
        var stack = this.events[name] || [];
        stack = stack.filter(function (rcb) { rcb.id !== cb.id } )
        this.events[name] = stack;
    },

    on: function(name, cb) {
        var stack = this.events[name] || [];
        stack.push(cb);

        seq += 1;
        cb.name = name;
        cb.id = seq;
        cb.un = function() { this.un(cb); };

        this.events[name] = stack;

        return cb;
    }
}

if (!core.RemoteObserver) {
    core.RemoteObserver = new _RemoteObserver();
}
