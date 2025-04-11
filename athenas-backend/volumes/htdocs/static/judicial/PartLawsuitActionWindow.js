
Ext._define('judicial.PartLawsuitActionWindow', {
    extend: 'judicial.PartLawsuitWindow',

    rest: 'judicial.PartLawsuitRestful',

    autoCreate: false,

    autoClose: true,

    signSuccessCallback: function() {
        this.afterSign = true;
        judicial.PartLawsuitActionWindow.superclass.signSuccessCallback.call(this);
        if(!this.autoClose)
            this.renderAfterSign();
    },

    readDataCallback: function(instance) {
        if(instance.read_only)
            this.renderAfterSign();
    },

    renderAfterSign: function() {
        this.registerButton().disable();
        this.cancelButton().setText('Fechar');
    },

    registerButton: function(cfg) {
        if(!this._registerButton)
            this._registerButton = Ext._create('Ext.Button', {
            text: 'Registrar',
            scope: this,
            handler: this.sign
        });

        return this._registerButton;
    },

    cancelButton: function(cfg) {
        if(!this._cancelButton)
            this._cancelButton = Ext._create('Ext.Button', {
            text: 'Cancelar',
            scope: this,
            handler: function() { this.close() }
        });

        return this._cancelButton;
    },

    getButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [
                '->',
                this.registerButton(),
                this.cancelButton()
            ]
        }

        return this._buttons
    },

    constructor: function(cfg) {
        cfg = (cfg || {});

        Ext.applyIf(
            cfg,
            {}
        );

        judicial.PartLawsuitActionWindow.superclass.constructor.call(this, cfg);

        this.on({
            scope: this,
            show: function() {
                if((this.autoCreate || false) && this.action === 'create') {
                    this.autoCreated = true;
                    this.save(true);
                }
            },
            close: function() {
                if(this.autoCreated && this.action === 'update' && this.oId && !this.afterSign) {
                    this.factoryRestful().remove(
                        this.oId,
                        {
                            externalCallback:
                            {
                                success: (this.callback.success || {fn: Ext.emptyFn})
                            }
                        },
                        false
                    );
                }
            }
        });
    }
});
