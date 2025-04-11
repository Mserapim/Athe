Ext.ns('toolkit.gep');

toolkit.gep.NotaComissao = Ext.extend(
    Ext.Window,
    {
        constructor: function(cfg) {
            cfg = (cfg ? cfg : {});
            Ext.apply(cfg, {
                title: 'Nota da Comissão de Avaliação',
                closable: true,
                resizable: true,
                modal: true,
                width: 500,
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

            toolkit.gep.NotaComissao.superclass.constructor.call(this, cfg);
            this.add(this.getFormPanel());
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
                            value: this.estagioprob_id
                        },
                        {
                            xtype: 'numberfield',
                            fieldLabel: 'Nota',
                            width:480,
                            name: 'nota',
                        },
                        {
                            xtype: 'ckeditor',
                            fieldLabel: 'Observação',
                            name: 'observacao',
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
            form.waitMsgTarget = this.getEl();
            form.submit({
                url: toolkit.util.Normalize.controller_action('GEPAvaliacaoEstagio', 'nota_comissao'),
                params: this.getParams(),
                scope: this,
                success: function(form, action) {
                    var message = action.result.message;
                    Ext.Msg.show({
                        title: 'Nota da Comissão de Avaliação',
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
                        title: 'Nota da Comissão de Avaliação',
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