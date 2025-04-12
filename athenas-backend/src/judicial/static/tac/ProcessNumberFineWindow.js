
Ext._define('judicial.tac.ProcessNumberFineWindow', {
    extend: 'Ext.Window',

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 130,
                items: [
                    {
                        xtype: 'textfield',
                        fieldLabel: 'Número do Procedimento',
                        name: 'process_number_fine',
                        width: 385
                    }
                ]
            });

        return this._formPanel;
    },

    save: function() {
        Ext.Msg.show({
            title: 'Marcando Execução',
            msg: 'Tem certeza que deseja marcar a execução para os itens selecionados?',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            scope: this,
            fn: function(btn) {
                if(btn == 'no') return;

                var rest = Ext._create('judicial.tac.ActivityRestful');
                var mask = new Ext.LoadMask(this.getEl(), {msg: 'salvando...'});

                mask.show();
                rest.fillProcessNumberFine(
                    this.activities,
                    this.getFormPanel().getForm().getValues(),
                    {
                        scope: this,
                        fn: function(rst) {
                            core.invokeCallback((this.success || {fn: Ext.emptyFn}), rst.message);
                            this.close();
                        }
                    },
                    {
                        scope: this,
                        fn: function(message) {
                            Ext.Msg.show({
                                title: 'Marcando execução',
                                msg: message,
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        }
                    },
                    {
                        fn: function() { mask.hide(); }
                    }
                );
            }
        });
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Marcando execução'
        });

        Ext.apply(cfg, {
            width: 550,
            border: false,
            items: [
                this.getFormPanel(cfg)
            ],
            buttons: [
                {
                    text: 'Salvar',
                    scope: this,
                    handler: function() {
                        this.save();
                    }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ]
        });

        judicial.tac.ProcessNumberFineWindow.superclass.constructor.call(this, cfg);

        this.on({
            scope: this,
            render: function() {
                if(cfg.values)
                    this.getFormPanel().getForm().setValues(cfg.values);
            }
        });
    }
});
