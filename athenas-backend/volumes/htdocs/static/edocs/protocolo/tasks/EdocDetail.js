Ext.ns('toolkit.edocs.protocolo.tasks');

toolkit.edocs.protocolo.tasks.EdocDetail = Ext.extend(
    Ext.Window,
    {
        getFormPanel: function(cfg) {
            if(!this.formPanel)
                this.formPanel = new Ext.form.FormPanel({
                    frame: true,
                    items: [
                        Ext._create('core.fields.ComboField', {
                            fieldLabel: 'Local de Origem',
                            hiddenName: 'workplace_origin',
                            displayField: 'description',
                            store: Ext._create('Ext.data.Store', {
                                proxy: Ext._create('Ext.data.HttpProxy', {
                                    url: core.callAction('EDOCManage', 'work_locations')
                                }),
                                reader: Ext._create('Ext.data.JsonReader', {
                                    totalProperty: 'count',
                                    root: 'collection',
                                    fields: [
                                        {name: 'pk', type: 'int'},
                                        {name: 'description', type: 'string'},
                                    ]
                                })
                            }),
                            width: 270,
                            allowBlank: true
                        }),
                        {
                            xtype: "rest-autocompletefield",
                            fieldLabel: "Local onde esteve",
                            allowBlank: true,
                            rest: "rh.generalorgan.Restful",
                            name: "workplace_destination"
                        },
                        {
                            width: 200,
                            allowBlank: true,
                            fieldLabel: "Assunto",
                            name: "subject",
                            xtype: "textfield",
                        },
                        {
                            width: 150,
                            allowBlank: true,
                            fieldLabel: "Código(para escolher um EDOC)",
                            name: "edoc_code",
                            xtype: "textfield",
                        },
                        {
                            width: 100,
                            allowBlank: true,
                            fieldLabel: "Enviado - A partir de",
                            name: "date_start",
                            xtype: "datefield",
                        },
                        {
                            width: 100,
                            allowBlank: true,
                            fieldLabel: "Enviado - Até",
                            name: "date_end",
                            xtype: "datefield",
                        },
                        {
                            width: 150,
                            xtype: 'combobox',
                            allowBlank: true,
                            store: [
                                [1, 'Todos'],
                                [2, 'Sim'],
                                [3, 'Não'],
                            ],
                            triggerAction: 'all',
                            hiddenName: 'finalized',
                            fieldLabel: 'Finalizado',
                            value: 1,
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
                    title: 'EDOC - Details',
                    closable: true,
                    resizable: false,
                    width: 400,
                    border: false,
                    modal: true,
                    controller: 'EDOCReportDetail',
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

            toolkit.edocs.protocolo.tasks.EdocDetail.superclass.constructor.call(this, cfg);
        }
    }
);