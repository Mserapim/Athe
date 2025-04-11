/**
 *
 **/
Ext._define('edocs.processo.config.Panel', {
    extend: 'core.RestfulPanel',


    rest: 'edocs.processo.config.Restful',

    _prepareSuccessCallback: function(callback) {
        var wnd = this;
        var success = callback.success;

        function foo(args) {
            core.invokeCallback(
                success,
                args
            );
        };

        callback.success = {
            fn: foo
        };

        return callback
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                    {
                        xtype:'fieldset',
                        title: 'Situação definida para',
                        autoHeight:true,
                        items:[
                        {
                            xtype: 'rest-combofield',
                            rest: 'edocs.processo.situacao.Restful',
                            fieldLabel: "Novo processo",
                            hiddenName: 'situacao_novo_processo',
                            triggerAction: 'all',
                            lazyRender: true,
                            lazyInit: true,
                            displayField: 'nome',
                            width: 550,
                        },
                        ]
                    },
                    {
                        xtype: 'button',
                        text: 'Salvar',
                        width: 100,
                        height: 25,
                        scope: this,
                        handler: this.save,
                    }
                ]
            });

        return this._formPanel;
    },

    getButtons: function(cfg) {
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                labelWidth:150,
                labelAlign:'right',
                action: 'update',
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                        }
                    }
                }
            }
        );

        Ext.apply(
            cfg,
            {

            }
        );

        edocs.processo.config.Panel.superclass.constructor.call(this, cfg);
    }
})
