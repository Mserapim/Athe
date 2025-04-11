Ext._define('rh.dayoff.attachment.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.dayoff.attachment.Restful',

    width: 530,

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getPublicationAttach(),
                    this.getProtocolAttach(),
                    this.getFileAttach(),
                    this.getSeiUrlAttach(),
                ]
            });

        return this._formPanel;
    },

    getProtocolAttach: function () {
        if (!this._protocolAttach) {
            this._protocolAttach = Ext._create('core.fields.AutocompleteField', {
                name: 'protocol',
                fieldLabel: 'Protocolo',
                allowBlank: true,
                rest: 'edocs.protocolo.masterbox.Restful'
            });
        }

        return this._protocolAttach;
    },

    getFileAttach: function () {
        if (!this._fileAttach) {
            this._fileAttach = Ext._create('core.fields.FileUploadField', {
                name: 'file_descriptor',
                fieldLabel: 'Arquivo',
                allowBlank: true,
                width: 400,
            });
        }

        return this._fileAttach;
    },

    getPublicationAttach: function () {
        if (!this._publicationAttach) {
            this._publicationAttach = Ext._create('core.fields.AutocompleteField', {
                name: 'publication',
                fieldLabel: 'Publica\u00e7\u00e3o',
                allowBlank: true,
                rest: 'rh.publicacao.Restful'
            });
        }

        return this._publicationAttach;

    },

    getSeiUrlAttach: function () {
        if (!this._seiUrlAttach)
            this._seiUrlAttach = Ext._create('Ext.form.TextField', {
                name: 'sei_url',
                fieldLabel: 'Sei Url',
                allowBlank: true,
                width: 395,
            });

        return this._seiUrlAttach;
    },

    constructor: function (cfg) {
        cfg = (cfg || {});

        Ext.applyIf(
            cfg,
            {}
        );
        rh.dayoff.attachment.Window.superclass.constructor.call(this, cfg);    }
});

