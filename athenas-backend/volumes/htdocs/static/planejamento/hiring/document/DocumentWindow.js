Ext._define('planning.hiring.document.DocumentWindow', {
    extend: 'core.RestfulWindow',
    rest: 'planning.hiring.document.DocumentRestful',
    width: 500,

    getContentField: function (cfg) {
        if (!this._contentField) {
            this._contentField = Ext._create('core.fields.FileUploadField', {
                fieldLabel: "Conteúdo",
                allowBlank: false,
                name: "file",
                loadingOwner: this,
                access: core.fields.FileUploadField.ACCESS.PUBLIC,
                width: 370,
                listeners: {
                    scope: this,
                    afterchange: function (input, instance) {
                        if (this.getTitleField().getValue() === '') {
                            var filename = instance.file_path.split(/.*[\/|\\]/)[1].replace(/\.[^/.]+$/, "");
                            var title = filename.charAt(0).toUpperCase() + filename.slice(1);
                            this.getTitleField().setValue(title);
                        }
                    }
                }
            });
        }

        return this._contentField;
    },

    getTitleField: function () {
        if (!this._titleField) {
            this._titleField = Ext._create('Ext.form.TextField', {
                fieldLabel: "Título",
                name: "title",
                allowBlank: false,
                maxLength: 150,
                selectOnFocus: true,
                width: 365
            });
        }

        return this._titleField;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                autoWidth: true,
                items: [
                    this.getContentField(),
                    this.getTitleField()
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function (instance) {
                    this.action = 'update';
                }
            }
        });

        planning.hiring.document.DocumentWindow.superclass.constructor.call(this, cfg);
    },
});