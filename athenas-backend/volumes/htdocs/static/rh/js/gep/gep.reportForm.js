Ext.ns('toolkit.gep');

toolkit.gep.ReportForm = Ext.extend(
    Ext.Window,
    {
        constructor: function(cfg, param) {
            cfg = (cfg ? cfg : {});
            this.id_servidor = param;
            Ext.apply(cfg, {
                title: 'Relatório de Avaliação',
                closable: true,
                resizable: true,
                modal: true,
                width: '400',
                border: false,
                buttons: [
                {
                    text: 'Gerar',
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

            toolkit.gep.ReportForm.superclass.constructor.call(this, cfg);
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
                        fieldLabel: 'Etapa do estágio',
                        xtype: 'numberfield',
                        allowBlank: false,
                        width:'350',
                        name: 'etapa'
                    },
                    {
                        fieldLabel: 'Servidor',
                        hidden:true,
                        name: 'servidor',
                        xtype: 'hidden', 
                        value: this.id_servidor
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
                url: toolkit.util.Normalize.controller_action('GEPGestorEstagio', this.action),
                params: this.getParams(),
                scope: this,
                success: function(form, action) {
                    // this.getStore().reload();
                    var servidor_pk = action.result.collection[0].pk_servidor;
                    var etapa = action.result.collection[0].etapa;
                    var cargo_pk = action.result.collection[0].cargo;
                    var questionario_avaliacao_pk = action.result.collection[0].questionario_avaliacao;
                    var questionario_manifestacao_pk = action.result.collection[0].questionario_manifestacao;

                    new toolkit.widget.ExtReportBuild('GEPPrintAvaliacaoChefe', '/to/mpe/rh/estagio_probatorio/avaliacao/rh_ep_main').runReport(
                        '', {servidor: servidor_pk, cargo: cargo_pk, etapa: etapa, questionario_avaliacao: questionario_avaliacao_pk, questionario_manifestacao : questionario_manifestacao_pk}
                    );
                    this.destroy();
                },
                failure: function(form, action) {
                    console.debug(action);

                    var message = ''
                    if(action.failureType == 'connect')
                        message = 'Não consegui acessar o recurso no servidor.'
                    else
                        message = action.result.message

                    Ext.Msg.show({
                        title: 'Configuração de Fator',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });

                    if(this.callback && this.callback.failure)
                        this.callback.failure.handler.call(this.callback.failure.scope ? this.callback.failure.scope : window);
                },
                waitMsg: 'aguarde...'
            })
        }
        
    }
);