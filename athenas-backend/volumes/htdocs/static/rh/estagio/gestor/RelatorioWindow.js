

Ext._define('estagio.gestor.RelatorioWindow', {
    extend: 'Ext.Window',

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                     {
                        fieldLabel: 'Etapa do estágio',
                        xtype: 'numberfield',
                        allowBlank: false,
                        width:'200',
                        name: 'etapa'
                    },
                    {
                        fieldLabel: 'Servidor',
                        hidden:true,
                        name: 'servidor',
                        xtype: 'hidden', 
                        value: cfg.params.servidor
                    },
                    {
                        fieldLabel: 'Cargo',
                        hidden:true,
                        name: 'cargo',
                        xtype: 'hidden', 
                        value: cfg.params.cargo
                    },
                    {
                        fieldLabel: 'Questionario Avaliação',
                        hidden:true,
                        name: 'questionario_avaliacao',
                        xtype: 'hidden', 
                        value: cfg.params.questionario_avaliacao
                    },
                    {
                        fieldLabel: 'Questionario Manifestação',
                        hidden:true,
                        name: 'questionario_manifestacao',
                        xtype: 'hidden', 
                        value: cfg.params.questionario_manifestacao
                    },
                ]
                    
            });
        return this._formPanel;
    },

    save: function(){
        var form = this.getFormPanel().getForm();
        // new toolkit.widget.ExtReportBuild('GepPrintAvaliacaoChefe', '/to/mpe/rh/estagio_probatorio/avaliacao/rh_ep_main').runReport(
        //     '', {
        //             servidor: form.getValues().servidor, 
        //             cargo: form.getValues().cargo, 
        //             etapa: form.getValues().etapa, 
        //             questionario_avaliacao: form.getValues().questionario_avaliacao, 
        //             questionario_manifestacao : form.getValues().questionario_manifestacao
        //         }
        // );
        engine.mq.Report.request({
            report: '/to/mpe/rh/estagio_probatorio/avaliacao/avaliacao',
            el: this.getEl(),
            waitMessage: 'Gerando os documentos...',
            params: {
                outfile: 'relatorio-' + form.getValues().servidor,
                report_name: 'Relatorio Estágio Probatório',
                servidor: form.getValues().servidor, 
                cargo: form.getValues().cargo, 
                etapa: form.getValues().etapa, 
                questionario_avaliacao: form.getValues().questionario_avaliacao, 
                questionario_manifestacao : form.getValues().questionario_manifestacao
            }
        });
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
        	cfg,
        	{
        		title: 'Relatório de Avaliação',
        		closable: true,
				height: 100,
        		width: 400
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
			}
		);
		estagio.gestor.RelatorioWindow.superclass.constructor.call(this, cfg);
    }
});