
Ext._define('core.fields.WebcamInputWindow', {
    extend: 'Ext.Window',

    getDevicesField: function(cfg) {
        if(!this._devicesField)
            this._devicesField = Ext._create('Ext.form.ComboBox', {
                xtype: 'combo',
                width: cfg.width - 210,
                store: this._factoryStore(cfg),
                valueField: 'deviceId',
                displayField: 'label',
                mode: 'local',
                editable: false,
                triggerAction: 'all',
                lazyInit: false,
                listeners: {
                    scope: this,
                    select: function(combo, record) {
                        if (record) {
                            this.selectDevice(record.get('deviceId'));
                        }
                    }
                }
            });

        return this._devicesField;
    },

    selectDevice: function(deviceId) {
        var deviceId = (deviceId || this.getDevicesField().getValue());
        var self = this;
        var player = self.getVideoDisplay().getEl().dom;
        var box = self.getVideoDisplay().getBox();
        var mask = new Ext.LoadMask(
            self.getEl(),
            { msg: 'inicando a webcam ...' }
        );

        mask.show();
        navigator.mediaDevices.getUserMedia({
            video: {
                deviceId: deviceId,
                width: { ideal: box.width },
                height: { ideal: box.height },
            }
        })
            .then(function(stream) {
                self.activeStream = stream;
                player.srcObject = stream;
                player.play();
                mask.hide();
            })
            .then(function() { localStorage.setItem('lastWebcamDeviceId', deviceId) })
            .catch(function(err) {
                mask.hide();
            });
    },

    capturePhoto: function() {
        if (this.activeStream) {
            var canvas = document.createElement('canvas');
            var player = this.getVideoDisplay().getEl().dom;
            var sx, sy;

            canvas.width = this.cropWidth || player.clientWidth;
            canvas.height = this.cropHeight || player.clientHeight;

            sx = (player.videoWidth - canvas.width) / 2.0;
            sy = (player.videoHeight - canvas.height) / 2.0;

            var context = canvas.getContext('2d');
            context.drawImage(
                player,
                sx, sy, canvas.width, canvas.height,
                0, 0, canvas.width, canvas.height
            );

            core.invokeCallback(
                (this.captureCallback || { fn: Ext.emptyFn }),
                canvas
            );
        } else {
            var defaultCallback = {
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Capturando foto',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            };

            core.invokeCallback(
                (this.captureCallback || defaultCallback),
                'Nenhuma camera foi selecionada, verifique se existe alguma camera selecionada e configurada'
            );
        }

        this.close();
    },

    _factoryToolbar: function(cfg) {
        return [
            'Selecione a camera :',
            this.getDevicesField(cfg),
            '-',
            {
                text: 'Capturar',
                scope: this,
                handler: function() { this.capturePhoto(); }
            }
        ];
    },

    _factoryStore: function(cfg) {
        var lastWebcamDeviceId = localStorage.getItem('lastWebcamDeviceId') || false;
        var self = this;
        var store = new Ext.data.Store({
            fields: [
                {name: 'deviceId', type: 'string'},
                {name: 'label', type: 'string'},
            ]
        });

        function isVideoInput(device) { return device.kind === 'videoinput' };

        navigator.mediaDevices.enumerateDevices()
            .then(function(devices) { return devices.filter(isVideoInput) })
            .then(function(devices) {
                var count = 0;

                devices.forEach(
                    function(device) {
                        count += 1
                        store.add(
                            new Ext.data.Record({
                                deviceId: device.deviceId,
                                label: device.label ? device.label : 'Webcam ' + count,
                            })
                        );
                    }
                );

                self.selectDevice(lastWebcamDeviceId);
            });

        return store;
    },

    renderCropMark: function() {
        var playerEl = this.getVideoDisplay().getEl().dom;
        var cropEl = document.createElement('div');
        var bodyEl = playerEl.parentNode;

        var style = {
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '100%',
            height: '100%',
            position: 'relative',
            left: 0,
            top: '-' + bodyEl.clientHeight + 'px',
            zIndex: 9999
        };

        var cropArea = document.createElement('div');

        if (this.cropWidth) {
            cropArea.style.width = this.cropWidth + 'px';
        } else {
            cropArea.style.width = '100%';
        }

        if (this.cropHeight) {
            cropArea.style.height = this.cropHeight + 'px';
        } else {
            cropArea.style.height = '100%';
        }

        cropArea.style.border = '1px solid #fff';
        cropEl.appendChild(cropArea);

        Object.keys(style)
            .forEach(function(attr) {
                cropEl.style[attr] = style[attr]
            });

        bodyEl.appendChild(cropEl);
    },

    getVideoDisplay: function(cfg) {
        if(!this._videoDisplay)
            this._videoDisplay = Ext._create('Ext.Container', {
                xtype: 'container',
                autoEl: 'video',
                style: { backgroundColor: '#000' },
                listeners: {
                    scope: this,
                    afterrender: function() {
                        this.renderCropMark();
                    }
                }
            });

        return this._videoDisplay;
    },

    constructor: function(cfg) {
        cfg = (cfg || {});

        Ext.applyIf(
            cfg,
            {
                height: 480,
                width: 720
            }
        );

        Ext.apply(
            cfg,
            {
                title: 'Capturar Imagem',
                tbar: this._factoryToolbar(cfg),
                resizable: false,
                modal: true,
                layout: 'fit',
                items: [
                    this.getVideoDisplay(cfg)
                ]
            }
        );

        core.fields.WebcamInputWindow.superclass.constructor.call(this, cfg);
        this.on({
            scope: this,
            destroy: function() {
                if (this.activeStream) {
                    this.activeStream.getVideoTracks()
                        .forEach(function(track) { track.stop() });
                }
            }
        });

        this.activeStream = null;
    }
});
