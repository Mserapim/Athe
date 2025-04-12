
Ext._define('core.fields.FileUploadField', {
    extend: 'Ext.form.CompositeField',

    xtype: 'core-fileuploadfield',

    statics: {
        ACCESS: {
            OWNER: 1,
            GROUP: 2,
            PUBLIC: 3
        }
    },

    getUploadField: function(cfg) {
        if(!this._uploadField)
            this._uploadField = Ext._create('Ext.form.TextField', {
                inputType: 'file',
                submitValue: false,
                hidden: true
            });

        return this._uploadField;
    },

    getValue: function() {
        return this.getValueField().getValue();
    },

    downloadURI: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._downloadURI = value;

            if(dispatch)
                this.downloadURIObserve();
        }

        return this._downloadURI;
    },

    downloadURIObserve: function() {
        var value = this.downloadURI();

        if(value) {
            console.info('downloadURI com valor');
        }
        else {
            console.info('downloadURI sem valor');
        }
    },

    hashId: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._hashId = value;

            if(dispatch)
                this.hashIdObserve();
        }

        return this._hashId;
    },

    hashIdObserve: function() {
        var value = this.hashId();
        this.fireEvent('changehashid', this, value);
    },

    refreshDisplayValue: function(pk) {
        Ext.Ajax.request({
            url: core.callAction('FileUploadController', 'get_file_info'),
            params: { pk: Number.parseInt(pk) },
            scope: this,
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);
                this.getDisplayField().setValue(rst.success ? rst.file_path : 'ERROR BUSCANDO DADOS');
                this.hashId(rst.file_hash);
                this.fireEvent('afterchange', this, rst);
            }
        });
    },

    setValue: function(value) {
        var olderValue = this.getValue();

        if (value === '' || value === null) {
            this.getDisplayField().setValue('');
        }
        else if (olderValue !== value) {
            this.refreshDisplayValue(value)
        }

        this.getValueField().setValue(value);
    },

    getDisplayField: function(cfg) {
        if(!this._displayField)
            this._displayField = Ext._create('Ext.form.TextField', {
                submitValue: false,
                readOnly: true,
                hidden: cfg.hideInputDisplay,
                width: (cfg.width || 150) - 83,
            });

        return this._displayField;
    },

    getValueField: function(cfg) {
        if(!this._valueField)
            this._valueField = Ext._create('Ext.form.TextField', {
                name: cfg.name,
                value: cfg.value,
                hidden: true
            });

        return this._valueField;
    },

    setWidth: function(width) {
        this.getMainPanel().setWidth(width);
        this.getDisplayField().setWidth(width - 83);
    },

    uploadURLData: function(filename, buffer) {
        var swap = buffer.split(',');
        var sign = swap[0];
        var content = swap[1];

        swap = sign.split(';')

        var mimeType = swap[0].split(':')[1];
        var me = this;
        var MBYTE = (1024 * 1024);
        var pos = 0;
        var chunk;
        var chunkSize = Number.parseInt((buffer.length / 8), 10);
        var progress = 0.0;

        var opts = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
        };

        me.fireEvent('startupload', me);
        fetch(core.callAction('FileUploadController', 'async_upload'), opts)
            .then(function(res) { return res.json() })
            .then(function(rst) {
                var chunks = [];
                var count = 0;
                var uuid = rst.uuid;

                while(pos < content.length) {
                    if ((pos + chunkSize) > content.length)
                        chunkSize = (content.length - pos);

                    chunks.push({
                        part: count,
                        start: pos,
                        limit: chunkSize,
                        inc: (chunkSize / content.length)
                    });

                    pos += chunkSize;
                    count += 1;
                }

                return Promise.all(
                    chunks.map(
                        function(info) {
                            opts = {
                                method: 'PUT',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                credentials: 'include',
                                body: JSON.stringify({
                                    content: content.substr(info.start, info.limit),
                                    method: 'store'
                                })
                            }

                            return fetch(core.callAction('FileUploadController', 'async_upload', [uuid, info.part]), opts)
                                .then(function(res) { return res.json() })
                                .then(function(rst) {
                                    progress += info.inc;

                                    core.invokeCallback(
                                        (me.progressCallback || { fn: Ext.emptyFn }),
                                        progress
                                    );

                                    me.fireEvent('progressupload', me, progress);

                                    return rst;
                                });
                        }
                    )
                )
                    .then(function(results) {
                        var flag = false;
                        var message = 'nada foi feito ainda';

                        results.forEach(
                            function(rst) {
                                if (!flag) {
                                    flag = (rst.success !== true);
                                }
                            }
                        );

                        if (flag)
                            return Promise.reject({
                                success: false,
                                message: message
                            });
                        else {
                            opts = {
                                method: 'PUT',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                credentials: 'include',
                                body: JSON.stringify({
                                    method: 'finish',
                                    filename: filename,
                                    mimetype: mimeType,
                                    access: me.access
                                })
                            };

                            return fetch(core.callAction('FileUploadController', 'async_upload', [uuid, 'finish']), opts)
                                .then(function(res) { return res.json() });
                        }
                    })
                    .then(function(rst) {
                        if (rst.success) {
                            me.setValue(rst.file_id);
                        } else {
                            Ext.Msg.show({
                                title: 'Enviando arquivo',
                                msg: rst.message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    });
            })
            .then(function() { me.fireEvent('finishupload') })
            .catch(function(err) {
                me.fireEvent('finishupload', me);
                Ext.Msg.show({
                    title: 'Enviando arquivo',
                    msg: 'Ocorreu um erro inesperado ao anexar o arquivo.Favor,tente novamente!',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });

                me.fireEvent('finishupload')
            })
    },

    openUpload: function() {
        var elDom = this.getUploadField().getEl().dom;
        var self = this;

        elDom.onchange = function() {
            var file = elDom.files[0];
            var reader = new FileReader();

            reader.onload = function(evt) {
                self.uploadURLData(
                    file.name,
                    evt.target.result
                );
            }

            reader.readAsDataURL(file);
        };

        elDom.click();
    },

    getClearButton: function(cfg) {
        if(!this._clearButton)
            this._clearButton = Ext._create('Ext.Button', {
                iconCls: 'icon-core icon-core-clear',
                scope: this,
                handler: function() { this.setValue(null) }
            });

        return this._clearButton;
    },

    getDownloadButton: function(cfg) {
        if(!this._downloadButton)
            this._downloadButton = Ext._create('Ext.Button', {
                iconCls: 'icon-core icon-core-document-arrow',
                scope: this,
                handler: function() {
                    open(
                        core.callAction('FileUploadController', 'get_file', this.hashId()),
                        '_self'
                    );
                }
            });

        return this._downloadButton;
    },

    _factoryMainButtons: function(cfg) {
        return [
            {
                xtype: 'button',
                iconCls: 'icon-core icon-core-attachment',
                scope: this,
                handler: function() { this.openUpload() }
            },
            this.getClearButton(cfg),
            this.getDownloadButton(cfg)
        ];
    },

    _factoryMainDisplayFields: function(cfg) {
        return [
            this.getValueField(cfg),
            this.getDisplayField(cfg)
        ];
    },

    getMainPanel: function(cfg) {
        if(!this._mainPanel)
            this._mainPanel = Ext._create('Ext.Panel', {
                layout: {
                    type: 'hbox',
                    defaultMargins: '2px',
                    padding: (cfg.hideInputDisplay ? '2' : '0'),
                    pack: (cfg.hideInputDisplay ? 'end' : 'start')
                },
                width: (cfg.width || 150),
                items: this._factoryMainDisplayFields(cfg).concat(this._factoryMainButtons(cfg))
            });

        return this._mainPanel;
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            access: core.fields.FileUploadField.ACCESS.GROUP,
            hideInputDisplay: false
        }),

        Ext.apply(cfg, {
            items: [
                {
                    xtype: 'panel',
                    items: [
                        this.getMainPanel(cfg),
                        this.getUploadField(cfg)
                    ]
                }
            ]
        });

        core.fields.FileUploadField.superclass.constructor.call(this, cfg);

        this.addEvents('afterchange');
        this.addEvents('changehashid');
        this.addEvents('progressupload');
        this.addEvents('starupload');
        this.addEvents('finishupload');

        if (this.loadingOwner) {
            var progress = Ext._create('Ext.ProgressBar', {
                text: 'carregando...',
                width: 160,
                style: {
                    margin: '5px'
                }
            });

            var wndProgress = Ext._create('Ext.Window', {
                header: false,
                modal: true,
                closable: false,
                frame: true,
                items: [ progress ]
            });

            this.on({
                scope: this,
                startupload: function(field) {
                    wndProgress.show(this.loadingOwner.getEl());
                },
                finishupload: function(field) {
                    wndProgress.hide();
                },
                progressupload: function(field, value) {
                    progress.updateProgress(value);
                }
            })
        }
    }
});
