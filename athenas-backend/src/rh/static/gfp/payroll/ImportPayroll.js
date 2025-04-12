Ext.ns('toolkit.rh.gfp.payroll.ImportPayroll');

toolkit.rh.gfp.payroll.ImportPayroll.Window = Ext.extend(
    Ext.Window,
    {
        constructor: function (cfg) {
            if (!cfg) cfg = {}

            Ext.applyIf(
                cfg,
                {
                    title: 'Importador de Folha de Pagamento',
                    closable: true,
                    resizable: false,
                    width: 500,
                    border: false,
                    modal: true,
                    controller: 'GFPImportPayroll',
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
                });

            toolkit.rh.gfp.payroll.ImportPayroll.Window.superclass.constructor.call(this, cfg);
        },

        getFormPanel: function (cfg) {
            if (!this.formPanel) {
                var now = new Date();
                this.formPanel = new Ext.form.FormPanel({
                    frame: true,
                    items: [
                        {
                            xtype: 'rest-autocompletefield',
                            fieldLabel: 'Selecione o Período',
                            name: 'period',
                            rest: 'rh.gfp.payroll.PeriodRestful',
                            allowBlank: false,
                        },
                        {
                            fieldLabel: 'Tipo de importação',
                            hiddenName: 'payroll_type',
                            name: 'payroll_type',
                            xtype: 'combo',
                            store: [
                                [1, 'DIÁRIAS'],
                            ],
                            value: 1,
                            typeAhead: true,
                            triggerAction: 'all',
                            allowBlank: false,
                            validateOnBlur: true,
                            width: 360
                        }
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
                    this.destroy();
                },
                scope: this,
                waitMsg: 'Aguarde ...'
            });
        },
    }
);
