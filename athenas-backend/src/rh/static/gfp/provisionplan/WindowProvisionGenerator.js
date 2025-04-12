Ext.ns('rh.gfp.provisionplan');

rh.gfp.provisionplan.WindowProvisionGenerator = Ext.extend(
    Ext.Window,
    {
        getFormPanel: function(cfg) {
            if(!this.formPanel)
                this.formPanel = new Ext.form.FormPanel({
                    frame: true,
                    items: [
                        {
                            fieldLabel: 'Plano de Provisão',
                            hiddenName: 'provisionplan',
                            name: 'provisionplan',
                            xtype: 'combo',
                            store: [
                                [1, 'FÉRIAS'],
                                [2, '13° SALÁRIO'],
                            ],
                            typeAhead: true,
                            width: 250,
                            triggerAction: 'all',
                            allowBlank: false,
                            validateOnBlur: true,
                        },
                        {
                            width: 250,
                            maxLength: 2,
                            allowBlank: false,
                            fieldLabel: "Mês",
                            name: "month",
                            xtype: "numberfield",
                        },
                        {
                            width: 250,
                            maxLength: 4,
                            allowBlank: false,
                            fieldLabel: "Ano",
                            name: "year",
                            xtype: "numberfield",
                        },
                        {
                            xtype: "rest-autocompletefield",
                            fieldLabel: "Servidor",
                            allowBlank: true,
                            rest: "rh.employee.Restful",
                            name: "employee"
                        },
                    ]
                });

            return this.formPanel;
        },

        execute: function(){
            var form = this.getFormPanel().getForm();

            form.waitMsgTarget = this.getFormPanel().getEl();
            form.submit({
                url: toolkit.util.Normalize.controller_action(this.controller, this.action),
                failure: function(form, action) {
                    var result = action.result;
                    alert(result.message);
                    this.close();
                },
                success: function(form, action){
                    var result = action.result;
                    alert(result.message);
                    this.close();
                },
                scope: this,
                waitMsg: 'Aguarde ...'
            });
        },

        constructor: function(cfg) {
            if(!cfg) cfg = {}

            Ext.applyIf(
                cfg,
                {
                    title: 'Gerador de provisão',
                    closable: true,
                    resizable: false,
                    width: 400,
                    border: false,
                    modal: true,
                    controller: 'PCProvisionManager',
                    action: 'generateProvision',
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