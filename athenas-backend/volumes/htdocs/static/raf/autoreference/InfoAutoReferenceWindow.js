Ext._define('raf.autoreference.InfoAutoReferenceWindow', {
    extend: 'Ext.Window',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
            });
        return this._formPanel;
    },

    autoreference: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._autoreference = value;

            if(dispatch) this.observerAutoReference();
        }

        return this._autoreference;
    },

    observerAutoReference: function() {
        var value = this.autoreference();
        if(value) {
        }else {
        }
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [

                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        this.close();
                    }
                }
            ];

        return this._buttons;
    },

    constructor: function(cfg) {

        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Visualizar auto referenciado',
            width: 900,
            height: 600,
        });

        Ext.apply(cfg, {
            items: this.getFormPanel(),
            buttons: [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ]
        });

        raf.autoreference.InfoAutoReferenceWindow.superclass.constructor.call(this, cfg);

        this.autoreference(this.params.autoreference);
    }
});
