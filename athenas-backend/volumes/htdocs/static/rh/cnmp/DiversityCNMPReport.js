Ext.ns('toolkit.rh.cnmp');

toolkit.rh.cnmp.DiversityCNMPReport = Ext.extend(
    Ext.Window,
    {
        getFormPanel: function (cfg) {
            if (!this.formPanel) {
                var now = new Date();
                this.formPanel = new Ext.form.FormPanel({
                    frame: true,
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
                    title: 'Gerador de relatório de diversidade CNMP',
                    closable: true,
                    resizable: false,
                    width: 500,
                    border: false,
                    modal: true,
                    controller: 'RHCNMPReport',
                    action: 'start',
                    items: [
                        this.getFormPanel(cfg),
                    ],
                    buttons: [
                        {
                            text: 'Gerar',
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

            toolkit.rh.cnmp.DiversityCNMPReport.superclass.constructor.call(this, cfg);
        }
    }
);
