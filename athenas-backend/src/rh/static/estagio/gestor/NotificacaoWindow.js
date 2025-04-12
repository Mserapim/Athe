

Ext._define('estagio.gestor.NotificacaoWindow', {
    extend: 'Ext.Window',

    width: 550,

    height: 300,

    getTexto: function(cfg){
        return 'O(a) Servidor(a): ' + cfg.params.nome + ' não concordou com sua avaliação referente a ' + cfg.params.etapa_atual + 'ª etapa do estágio probatório. Favor reconsiderar a avaliação. Qualquer dúvida entre em contato com o Departamento de Recursos Humanos.' 
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: 'hidden',
                        name: 'pk',
                        value: cfg.params.pk
                    },
                    {
                        xtype: 'textarea',
                        fieldLabel: 'Mensagem',
                        name: 'mensagem',
                        width: 380,
                        height: 200,
                        value: this.getTexto(cfg)
                    }
                ]
                    
            });
        return this._formPanel;
    },

    save: function(){
        var form = this.getFormPanel().getForm();
        var rest = Ext._create('estagio.gestor.EstagioProbatorioServidorRestful', {});
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Persistindo dados...'});

        mask.show();
        rest.doRequest(
            rest.getRoute('notifica_divergencia', false, 'POST', {
                scope: this,
                params: {
                    pk: form.getValues().pk,
                    mensagem: form.getValues().mensagem,
                },
                callback: function() {
                    mask.hide();
                    mask = undefined;
                },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(rst.success) {
                        this.destroy();
                    }
                    else
                        Ext.Msg.show({
                            title: 'Atenção',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK,
                            msg: rst.message
                        });
                },
                failure: function(xhr) {
                    Ext.Msg.show({
                        title: 'Atenção',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: 'Recurso indisponível no momento.'
                    });
                },
            })
        );
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
        	cfg,
        	{
        		title: 'Notificação',
        		closable: true,
        	}
        );
		Ext.apply(
			cfg,
			{
				border: false,
				layout: 'fit',
				items: [
					this.getFormPanel(cfg)
				],
                buttons: [
                    {
                        text: 'Enviar',
                        scope: this,
                        handler: this.save
                    },
                    {
                        text: 'Cancelar',
                        scope: this,
                        handler: this.destroy
                    }
                ]   
			}
		);

		estagio.gestor.NotificacaoWindow.superclass.constructor.call(this, cfg);
    }
});