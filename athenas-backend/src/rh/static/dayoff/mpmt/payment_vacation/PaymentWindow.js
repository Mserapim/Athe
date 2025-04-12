Ext._define('rh.dayoff.mpmt.payment_vacation.PaymentWindow', {
    extend: 'rh.dayoff.mpmt.activity.Window',

    width: 750,

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items:[
                    {
                        xtype: 'fieldset',
                        title: 'Pagamento - Usufruto',
                        layout: 'form',
                        style: 'text-align: center !important',
                        items: [

                            {
                                layout: 'column',
                                items: [
                                    {
                                        columnWidth: '0.4',
                                        layout: 'form',
                                        items: [
                                            {
                                                fieldLabel: 'Competência de Pagamento',
                                                name: 'competence',
                                                xtype: 'textfield'
                                            },
                                            {
                                                fieldLabel: 'Numero de Parcelas',
                                                name: 'payment_installments',
                                                xtype: 'numberfield'
                                            },
                                        ]
                                    },
                                    {
                                        columnWidth: '0.6',
                                        layout: 'form',
                                        
                                        items: [
                                            {
                                                fieldLabel: 'Observação',
                                                xtype: 'textfield',
                                                name: 'observation',
                                                height: 200,
                                                width:300
                                            },
                                        ]
                                    }
                                ]
                            },
                          
                        ]
                    },
                ]
            });

        return this._formPanel;
    },



    save: function (cfg) {
        var values = this.getFormPanel().getForm().getValues();
        var params = {
            usufruct: cfg.usufruct,
            activity: cfg.activity,
            competence: values.competence,
            qtd_parcel: values.payment_installments,
            observation: values.observation,
        };
        this.executeAction(cfg.actionCustom, params)

    },

    getButtons: function (cfg) {
        if (!this._buttons)
            this._buttons = [
                {
                    id: 'btn_save',
                    text: '<b>Salvar</b>',
                    scope: this,
                    handler: function () {
                        this.save(cfg);
                    }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function () {
                        this.close();
                    }
                }
            ];
        return this._buttons;
    },

    executeAction: function(method, params){
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action('DAYOFFPaymentVacation', method),
            params,
            success: function(request) {
                var obj = Ext.decode(request.responseText);
                var icon = obj.success == true ? Ext.Msg.INFO : Ext.Msg.ERROR;
                Ext.Msg.show({
                    width:"400px",
                    title: this.title,
                    icon: icon,
                    buttons: Ext.Msg.OK,
                    msg: obj.message
                });

                if(obj.success == true){ 
                    this.close();
                    this.getStore().reload(); 
                }
            },
            failure: function() {
                Ext.Msg.show({
                    title: this.title,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Recurso indisponivel no momento, tente novamente mais tarde.'
                });
            },
            scope: this
        });

    },

  
});
