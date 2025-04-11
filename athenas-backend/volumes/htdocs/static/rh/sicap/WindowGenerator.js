Ext.ns('toolkit.rh.sicap');

toolkit.rh.sicap.WindowGenerator = Ext.extend(
    Ext.Window,
    {
        getFormPanel: function (cfg) {
            if (!this.formPanel) {
                var now = new Date();
                this.formPanel = new Ext.form.FormPanel({
                    frame: true,
                    items: [
                        {
                            fieldLabel: 'Mês',
                            hiddenName: 'month',
                            name: 'month',
                            xtype: 'combo',
                            store: [
                                [1, 'JANEIRO'],
                                [2, 'FEVEREIRO'],
                                [3, 'MARÇO'],
                                [4, 'ABRIL'],
                                [5, 'MAIO'],
                                [6, 'JUNHO'],
                                [7, 'JULHO'],
                                [8, 'AGOSTO'],
                                [9, 'SETEMBRO'],
                                [10, 'OUTUBRO'],
                                [11, 'NOVEMBRO'],
                                [12, 'DEZEMBRO'],
                            ],
                            typeAhead: true,
                            triggerAction: 'all',
                            allowBlank: false,
                            validateOnBlur: true,
                            width: 360
                        },
                        {
                            maxLength: 4,
                            allowBlank: false,
                            fieldLabel: 'Ano',
                            name: 'year',
                            value: now.getFullYear(),
                            xtype: 'numberfield',
                            width: 360
                        },
                        {
                            fieldLabel: 'Arquivo de Pagamentos',
                            xtype: 'ged-fileuploadfield',
                            name: 'paymentfile',
                            allowBlank: true,
                            width: 470
                        },
                    ]
                });
            }
            return this.formPanel;
        },

        execute: function () {
            var form = this.getFormPanel().getForm();

            form.waitMsgTarget = this.getFormPanel().getEl();
            form.submit({
                url: toolkit.util.Normalize.controller_action(this.controller, this.action),
                failure: function (form, action) {
                    var result = action.result;
                    alert(result.message);
                },
                success: function (form, action) {
                    var result = action.result;
                    alert(result.message);
                },
                scope: this,
                waitMsg: 'Aguarde ...'
            });
        },

        constructor: function (cfg) {
            if (!cfg) cfg = {}

            Ext.applyIf(
                cfg,
                {
                    title: 'Gerador de arquivos do SICAP AP',
                    closable: true,
                    resizable: false,
                    width: 500,
                    border: false,
                    modal: true,
                    controller: 'RHSicapApGenerator',
                    action: 'start',
                    items: [
                        this.getFormPanel(cfg),
                    ],
                    buttons: [
                        {
                            text: 'Executar',
                            scope: this,
                            handler: this.execute
                        },
                        {
                            text: 'Cancelar',
                            scope: this,
                            handler: this.destroy
                        }
                    ]
                }
            );

            toolkit.rh.sicap.WindowGenerator.superclass.constructor.call(this, cfg);
        }
    }
);
