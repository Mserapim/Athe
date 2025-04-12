Ext.ns('toolkit.gep');

toolkit.gep.IntegranteComissaoForm = Ext.extend(
    Ext.Window,
    {
        constructor: function(cfg , comissao) {
            this.pk_comissao = comissao;
            // console.log(this.pk_comissao);
            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                title: 'Integrantes da Comissão',
                closable: true,
                resizable: true,
                modal: true,
                width: '400',
                border: false,
                buttons: [
                {
                    text: 'Salvar',
                    scope: this,
                    handler: this.save
                },
                {
                    text: 'Cancelar',
                    scope: this,
                    handler: this.destroy
                }
                ]   
            });

            toolkit.gep.IntegranteComissaoForm.superclass.constructor.call(this, cfg);
            this.add(this.getFormPanel());
            if(this.values) this.getFormPanel().getForm().setValues(this.values);
            // console.log(this.values)
        },

        getFormPanel: function() {
            if(!this._formPanel)
                this._formPanel = new Ext.form.FormPanel({
                    frame: true,
                    labelAlign: 'top',
                    items: [
                        {
                            xtype:'hidden',
                            name: 'pk_comissao',
                            value: this.pk_comissao
                        },
                        {
                            displayField: 'description', 
                            name:'integrante',
                            fieldLabel: 'Integrante', 
                            allowBlank: false, 
                            hiddenName: 'integrante', 
                            valueField: 'pk', 
                            triggerAction: 'all', 
                            queryAction: 'query', 
                            hideTrigger: true, 
                            queryParam: 'keyword', 
                            crudController: 'RHServidor', 
                            xtype: 'autocompletefield',
                            width: 450
                        },
                        {
                            xtype: 'combo',
                            width:350,
                            allowBlank: false, 
                            hiddenName: 'tipo_integrante',
                            fieldLabel: 'Tipo de Integrante',
                            store: [
                                [ 1, 'PRESIDENTE'],
                                [ 2, 'SECRETÁRIO'],
                                [ 3, 'INTEGRANTE'],
                                [ 4, 'SUPLENTE'],
                            ],
                            triggerAction: 'all',
                        },
                        {
                            xtype: 'combo',
                            width:350,
                            allowBlank: true, 
                            hiddenName: 'impedimento',
                            fieldLabel: 'Impedido',
                            store: [
                                [ 1, 'NÃO'],
                                [ 2, 'SIM'],
                            ],
                            triggerAction: 'all',
                        },
                    ]
                });
        
            return this._formPanel;
        },

        getParams: function() {
            return this.params;
        },

        save: function() {
            var form = this.getFormPanel().getForm();
            //console.log(this.action);
            form.waitMsgTarget = this.getEl();
            form.submit({
                url: toolkit.util.Normalize.controller_action('GEPComissaoAvaliadora', this.action),
                params: this.getParams(),
                scope: this,
                success: function(form, action) {
                    // this.getStore().reload();
                    if(this.callback && this.callback.success)
                        this.callback.success.handler.call(this.callback.success.scope ? this.callback.success.scope : window);
                    Ext.Msg.alert('Sucesso', 'Dados salvos com sucesso!');
                    this.destroy()
                },
                failure: function(form, action) {
                    // console.debug(action);

                    var message = ''
                    if(action.failureType == 'connect')
                        message = 'Não consegui acessar o recurso no servidor.'
                    else
                        message = action.result.message

                    Ext.Msg.show({
                        title: 'Integrante da Comissão',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });

                    if(this.callback && this.callback.failure)
                        this.callback.failure.handler.call(this.callback.failure.scope ? this.callback.failure.scope : window);
                },
                waitMsg: 'Salvando dados...'
            })
        }
        
    }
    );