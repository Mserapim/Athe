/**
 *
 **/
Ext._define('edocs.processo.ImprimirForm', {
    extend: 'core.RestfulWindow',

    // rest: 'edocs.processo.Restful',

    actionTitles: {
        create: 'Impressão de Etiqueta',
        update: 'Impressão de Etiqueta',
        remove: 'Remover',
        read: 'Carregar'
    },

    width: 530,

    getFormPanel: function() {
        var width = 550;
        var height_multiselect_geral = 100;
        var height_multiselect_departamento = 100;
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [
                    new Ext.TabPanel({
                        activeTab: 0,
                        // width: 510,
                        height: 100,
                        border: false,
                        items: [
                            {
                                xtype: "panel",
                                layout: "form",
                                title: "Informações",
                                border: false,
                                style: "margin: 5pt",
                                defaults: { width: 370 },
                                labelWidth: 120,
                                items: [
                                    {
                                        allowBlank: false,
                                        hiddenName: "impressora",
                                        fieldLabel: "Impressora",
                                        xtype: "combo",
                                        displayField: "description",
                                        valueField: "id",
                                        store: new Ext.data.JsonStore({
                                            root: "result",
                                            url: toolkit.util.Normalize.controller_action(
                                                "EDOCBox",
                                                "get_store",
                                                ["impressora"]
                                            ),
                                            fields: [ "id", "description"],
                                            autoLoad: true
                                        }),
                                        triggerAction: "all",
                                        mode: 'local'
                                    },
                                    {
                                        fieldLabel: "Quantidade",
                                        hiddenName: "quantidade",
                                        xtype: "combo",
                                        store: new Ext.data.SimpleStore({
                                            fields: ["id", "desc"],
                                            data: [['1', '1'], ['2', '2'],
                                                    ['3', '3'], ['4', '4'],
                                                    ['5', '5'], ['6', '6'],
                                                    ['7', '7'], ['8', '8'],
                                                    ['9', '9'], ['10', '10']]
                                        }),
                                        valueField: "id",
                                        displayField: "desc",
                                        mode: "local",
                                        triggerAction: "all"
                                    }
                                ]
                            },
                        ]
                    })
                ]
            });

        return this._formPanel;
    },

    getButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [
                {
                    text: "Imprimir",
                    handler: this.imprimir,
                    scope: this
                },
                {
                    text: "Fechar",
                    handler: function() { this.destroy(); },
                    scope: this
                }
            ];
        }

        return this._buttons;
    },

    imprimir: function() {
        var form = this.getFormPanel().getForm();
        conf = {
            params: Ext.applyIf(
                form.getValues(),
                this.getParams()
            ),
            scope: this,
            method: 'POST',
            url: core.callAction("EpadMovimentacao", "action_imprimir_etiqueta"),
            success: function(request) {
                var rst = Ext.decode(request.responseText);
                if(rst.success) {
                    this.destroy()
                }
                else {
                    Ext.Msg.show({
                        title: 'Imprimir Etiqueta',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: rst.message
                    });
                }
            },
            failure: function(request) {
                console.debug('Falha na requisição')
            },
        }
        Ext.Ajax.request(conf)
    },
});
