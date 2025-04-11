Ext._define('rh.falta.employee.ProcessaFaltaWindow', {
    extend: 'Ext.Window',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = new Ext.form.FormPanel({
                border: false,
                frame: true,
                scope: this,
                items: [
                    this.getReference(),
                    this.getTipo(),
                ],
                buttons: [
                    {
                        text: 'Processar',
                        scope: this,
                        handler: this.doSubmit
                    },
                    {
                        text: 'Cancelar',
                        scope: this,
                        handler: this.destroy
                    }
                ]                

            });
    
        return this._formPanel;
    },

    getReference: function() {
        if (!this._yearfield) {
            this._yearfield = Ext._create('core.fields.ComboField', {
                fieldLabel: "Competência",
                hiddenName: "year",
                anchor:'99%',
                // value:new Date().getFullYear(),
                displayField: 'description',
                store: Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('PONTFalta', 'get_reference')
                        // url: core.callAction('PVFSendPointSheet', 'get_reference')
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
                autoLoad: true
            });
        }

        return this._yearfield;
    },

    getTipo: function() {
        if (!this._tipo) {
            this._tipo = Ext._create('Ext.form.RadioGroup', {
                xtype:'radiogroup',
                fieldLabel: 'Tipo de Processamento',
                columns: 2,
                items: [
                    {
                        xtype:'radio',
                        inputValue: 1,
                        boxLabel: 'Todos',
                        name: 'tipo',
                        checked: true,
                        allowBlank: true,
                    },
                    {
                        xtype:'radio',
                        inputValue: 2,
                        boxLabel: 'Selecionado',
                        name: 'tipo',
                        allowBlank: true, 
                    },
                ]
            });
        }

        return this._tipo;
    },

    doSubmit: function(){
        if (this.getReference().getValue()) {
            if (this.getTipo().getValue().inputValue == 1 || (this.getTipo().getValue().inputValue == 2 && this.employee_id != '')) {
                var form = this.getFormPanel().getForm();
                
                Ext.Ajax.request({
                    url: toolkit.util.Normalize.controller_action('PONTFalta', 'processar_faltas'),
                    scope: this,
                    params: {
                        employee: this.employee_id,
                        reference: this.getReference().lastSelectionText,
                        tipo: this.getTipo().getValue().inputValue
                    },
                    success: function(request,form, action) {
                        var rst = Ext.decode(request.responseText);
                        Ext.Msg.show({
                            title: 'Processando faltas...',
                            msg: rst.message,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK
                        });
                        this.destroy();
                    },
                    failure: function(form, action) {
                        if(action.failureType == 'client')
                            message = 'Erro de comunicação com servidor, tente novamente mais tarde.'
                        else
                            message = action.result.message;

                        Ext.Msg.show({
                            title: this.title,
                            msg: message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                });
            } else Ext.Msg.show({
                msg: 'Selecione o Servidor na tela anterior.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            })
        } else Ext.Msg.show({
            msg: 'Selecione a Competência.',
            icon: Ext.Msg.ERROR,
            buttons: Ext.Msg.OK
        })
    },

    constructor: function(cfg) {
        cfg = (cfg ? cfg : {});

        Ext.apply(cfg, {
            title: 'Processar Faltas',
            modal: true,
            resizable: false,
            width: 500,
            items: this.getFormPanel()
        });

        rh.falta.employee.ProcessaFaltaWindow.superclass.constructor.call(this, cfg);
    }
});