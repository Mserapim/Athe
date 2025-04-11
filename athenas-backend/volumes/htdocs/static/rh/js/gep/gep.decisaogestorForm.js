Ext.ns('toolkit.gep');

toolkit.gep.DecisaoGestorForm = Ext.extend(
    Ext.Window,
    {
        constructor: function(cfg) {
            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                title: 'Decisão',
                closable: true,
                resizable: true,
                modal: true,
                width: '500',
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

            toolkit.gep.DecisaoGestorForm.superclass.constructor.call(this, cfg);
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
                            xtype: 'combo',
                            width:450,
                            allowBlank: false,
                            hiddenName: 'decisao',
                            fieldLabel: 'Decisão',
                            store: [
                                [ 1, 'HOMOLOGA A RECOMENDAÇÃO DA COMISSÃO'],
                                [ 2, 'NÃO HOMOLOGA A RECOMENDAÇÃO DA COMISSÃO'],
                            ],
                            triggerAction: 'all',
                        },
                        {
                            xtype: 'ckeditor',
                            fieldLabel: 'Fundamentação',
                            name: 'fundamentacao',
                            autoWidth: true,
                            height: 200,
                        }
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
                url: toolkit.util.Normalize.controller_action('GEPDecisaoChefeOrgao', this.action),
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
                        title: 'Decisão',
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