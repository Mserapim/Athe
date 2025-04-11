Ext.ns('toolkit.gep');

toolkit.gep.Notificacao = Ext.extend(
    Ext.Window,
    {
        constructor: function(cfg) {
            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                title: 'Notificação',
                closable: true,
                resizable: true,
                modal: true,
                width: 400,
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

            toolkit.gep.Notificacao.superclass.constructor.call(this, cfg);
            this.add(this.getFormPanel());
            // if(this.values) this.getFormPanel().getForm().setValues(this.values);
        },

        getTexto: function(){
            return 'O(a) Servidor(a): ' + this.servidor_nome + ' não concordou com sua avaliação referente a ' + this.etapa_atual + 'ª etapa do estágio probatório. Favor reconsiderar a avaliação. Qualquer dúvida entre em contato com o Departamento de Recursos Humanos.' 
        },

        getFormPanel: function() {
            if(!this._formPanel)
                this._formPanel = new Ext.form.FormPanel({
                    frame: true,
                    labelAlign: 'top',
                    items: [
                        {
                            xtype: 'hidden',
                            name: 'estagioprob_id',
                            value: this.servidor_id
                        },
                        {
                            xtype: 'textarea',
                            fieldLabel: 'Mensagem',
                            name: 'mensagem',
                            width: 380,
                            height: 100,
                            value: this.getTexto()
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
            form.waitMsgTarget = this.getEl();
            form.submit({
                url: toolkit.util.Normalize.controller_action('GEPAvaliacaoEstagio', 'notifica_divergencia'),
                params: this.getParams(),
                scope: this,
                success: function(form, action) {
                    var message = action.result.message;
                    Ext.Msg.show({
                        title: 'Notificação',
                        msg: message,
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                    this.destroy()
                    if(this.callback && this.callback.success)
                        this.callback.success.handler.call(this.callback.success.scope ? this.callback.success.scope : window);
                },
                failure: function(form, action) {
                    // console.debug(action);
                    var message = ''
                    if(action.failureType == 'connect')
                        message = 'Não consegui acessar o recurso no servidor.'
                    else
                        message = action.result.message

                    Ext.Msg.show({
                        title: 'Notificação',
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